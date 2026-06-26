import platform
import subprocess
import json
import re
import sys
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CPUInfo:
    name: str
    physical_cores: int
    logical_cores: int
    max_freq_ghz: float
    architecture: str
    is_apple_silicon: bool = False


@dataclass
class RAMInfo:
    total_gb: float
    available_gb: float


@dataclass
class GPUInfo:
    name: str
    vram_gb: float
    vendor: str
    vram_capped: bool = False  # WMI 32-bit cap warning


@dataclass
class StorageInfo:
    total_gb: float
    free_gb: float
    drive: str


@dataclass
class SystemInfo:
    cpu: CPUInfo
    ram: RAMInfo
    gpus: List[GPUInfo]
    storage: StorageInfo
    os_name: str
    os_version: str


def _detect_vendor(name: str) -> str:
    name_lower = name.lower()
    if any(k in name_lower for k in ["nvidia", "geforce", "rtx", "gtx", "quadro", "tesla"]):
        return "NVIDIA"
    if any(k in name_lower for k in ["amd", "radeon", "rx ", "vega", "navi", "rdna"]):
        return "AMD"
    if any(k in name_lower for k in ["intel", "iris", "uhd", "arc"]):
        return "Intel"
    if any(k in name_lower for k in ["apple", "m1", "m2", "m3", "m4"]):
        return "Apple"
    return "Unknown"


def _get_nvidia_gpus() -> List[GPUInfo]:
    """Use nvidia-smi for accurate VRAM (NVIDIA only)."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=8
        )
        if result.returncode == 0:
            gpus = []
            for line in result.stdout.strip().splitlines():
                parts = line.split(", ")
                if len(parts) == 2:
                    name = parts[0].strip()
                    vram_mb = float(parts[1].strip())
                    gpus.append(GPUInfo(
                        name=name,
                        vram_gb=round(vram_mb / 1024, 1),
                        vendor="NVIDIA"
                    ))
            return gpus
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass
    return []


def _get_gpus_windows() -> List[GPUInfo]:
    """Detect all GPUs on Windows via PowerShell/WMI."""
    nvidia = _get_nvidia_gpus()
    nvidia_names = {g.name.lower() for g in nvidia}

    other_gpus: List[GPUInfo] = []
    try:
        ps_cmd = (
            'Get-WmiObject Win32_VideoController | '
            'Select-Object Name, AdapterRAM | '
            'ConvertTo-Json -Compress'
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout.strip():
            raw = result.stdout.strip()
            data = json.loads(raw)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                name = (item.get("Name") or "Unknown GPU").strip()
                if not name or name.lower() in nvidia_names:
                    continue
                vram_bytes = item.get("AdapterRAM") or 0
                vram_gb = round(vram_bytes / (1024 ** 3), 1)
                # WMI 32-bit cap: 4294967296 bytes = exactly 4GB signals overflow
                capped = (vram_bytes == 4294967296)
                vendor = _detect_vendor(name)
                other_gpus.append(GPUInfo(
                    name=name,
                    vram_gb=vram_gb,
                    vendor=vendor,
                    vram_capped=capped
                ))
    except Exception:
        pass

    return nvidia + other_gpus


def _get_gpus_linux() -> List[GPUInfo]:
    nvidia = _get_nvidia_gpus()
    if nvidia:
        return nvidia
    # Try lspci for AMD/Intel
    try:
        result = subprocess.run(["lspci"], capture_output=True, text=True, timeout=5)
        gpus = []
        for line in result.stdout.splitlines():
            if "VGA" in line or "Display" in line or "3D" in line:
                name = re.sub(r"^[0-9a-f:.]+\s+\w+\s+controller:\s+", "", line, flags=re.I)
                vendor = _detect_vendor(name)
                gpus.append(GPUInfo(name=name.strip(), vram_gb=0.0, vendor=vendor))
        return gpus
    except Exception:
        return []


def _get_gpus_macos() -> List[GPUInfo]:
    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType", "-json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            displays = data.get("SPDisplaysDataType", [])
            gpus = []
            for d in displays:
                name = d.get("sppci_model", "Unknown GPU")
                vram_str = d.get("spdisplays_vram", "0 MB")
                match = re.search(r"(\d+)\s*(GB|MB)", vram_str, re.I)
                vram_gb = 0.0
                if match:
                    val = float(match.group(1))
                    unit = match.group(2).upper()
                    vram_gb = val if unit == "GB" else round(val / 1024, 1)
                vendor = _detect_vendor(name)
                is_apple = "Apple" in name or vendor == "Apple"
                gpus.append(GPUInfo(name=name, vram_gb=vram_gb, vendor="Apple" if is_apple else vendor))
            return gpus
    except Exception:
        pass
    return []


def _get_cpu_info() -> CPUInfo:
    try:
        import psutil
        import cpuinfo
        info = cpuinfo.get_cpu_info()
        freq = psutil.cpu_freq()
        name = info.get("brand_raw", platform.processor() or "Unknown CPU")
        arch = info.get("arch", platform.machine())
        max_freq = round((freq.max if freq and freq.max else (freq.current if freq else 0)) / 1000, 2)
        is_apple = "Apple" in name or "M1" in name or "M2" in name or "M3" in name or "M4" in name
        return CPUInfo(
            name=name,
            physical_cores=psutil.cpu_count(logical=False) or 1,
            logical_cores=psutil.cpu_count(logical=True) or 1,
            max_freq_ghz=max_freq,
            architecture=arch,
            is_apple_silicon=is_apple,
        )
    except Exception:
        return CPUInfo(
            name=platform.processor() or "Unknown CPU",
            physical_cores=1,
            logical_cores=1,
            max_freq_ghz=0.0,
            architecture=platform.machine(),
        )


def _get_ram_info() -> RAMInfo:
    try:
        import psutil
        mem = psutil.virtual_memory()
        return RAMInfo(
            total_gb=round(mem.total / (1024 ** 3), 1),
            available_gb=round(mem.available / (1024 ** 3), 1),
        )
    except Exception:
        return RAMInfo(total_gb=0.0, available_gb=0.0)


def _get_storage_info() -> StorageInfo:
    try:
        import psutil
        best = None
        # On Windows, only physical drives (cdrom=False) to avoid optical drives
        for part in psutil.disk_partitions(all=False):
            if not part.mountpoint:
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                if best is None or usage.free > best[0]:
                    best = (usage.free, usage.total, part.mountpoint)
            except (PermissionError, OSError):
                continue
        if best and best[1] > 0:
            return StorageInfo(
                free_gb=round(best[0] / (1024 ** 3), 1),
                total_gb=round(best[1] / (1024 ** 3), 1),
                drive=best[2],
            )
    except Exception:
        pass
    # Fallback: try C:\ directly on Windows
    try:
        import psutil
        usage = psutil.disk_usage("C:\\")
        return StorageInfo(
            free_gb=round(usage.free / (1024 ** 3), 1),
            total_gb=round(usage.total / (1024 ** 3), 1),
            drive="C:\\",
        )
    except Exception:
        pass
    return StorageInfo(total_gb=0.0, free_gb=0.0, drive="Unknown")


def scan_hardware() -> SystemInfo:
    os_name = platform.system()

    if os_name == "Windows":
        gpus = _get_gpus_windows()
    elif os_name == "Darwin":
        gpus = _get_gpus_macos()
    else:
        gpus = _get_gpus_linux()

    # Deduplicate by name
    seen = set()
    unique_gpus = []
    for g in gpus:
        if g.name not in seen:
            seen.add(g.name)
            unique_gpus.append(g)

    return SystemInfo(
        cpu=_get_cpu_info(),
        ram=_get_ram_info(),
        gpus=unique_gpus,
        storage=_get_storage_info(),
        os_name=os_name,
        os_version=platform.version(),
    )
