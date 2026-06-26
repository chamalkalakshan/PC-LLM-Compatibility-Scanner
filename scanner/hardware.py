import platform
import subprocess
import json
from dataclasses import dataclass, field
from typing import List


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
    vram_capped: bool = False


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
    n = name.lower()
    if any(k in n for k in ["nvidia", "geforce", "rtx", "gtx", "quadro", "tesla"]):
        return "NVIDIA"
    if any(k in n for k in ["amd", "radeon", "rx ", "vega", "navi", "rdna"]):
        return "AMD"
    if any(k in n for k in ["intel", "iris", "uhd", "arc"]):
        return "Intel"
    return "Unknown"


def _get_nvidia_gpus() -> List[GPUInfo]:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=8,
        )
        if result.returncode == 0:
            gpus = []
            for line in result.stdout.strip().splitlines():
                parts = line.split(", ")
                if len(parts) == 2:
                    gpus.append(GPUInfo(
                        name=parts[0].strip(),
                        vram_gb=round(float(parts[1].strip()) / 1024, 1),
                        vendor="NVIDIA",
                    ))
            return gpus
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass
    return []


def _get_gpus_windows() -> List[GPUInfo]:
    nvidia = _get_nvidia_gpus()
    nvidia_names = {g.name.lower() for g in nvidia}
    other: List[GPUInfo] = []
    try:
        ps = (
            "Get-WmiObject Win32_VideoController | "
            "Select-Object Name, AdapterRAM | ConvertTo-Json -Compress"
        )
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode == 0 and r.stdout.strip():
            data = json.loads(r.stdout.strip())
            if isinstance(data, dict):
                data = [data]
            for item in data:
                name = (item.get("Name") or "Unknown GPU").strip()
                if not name or name.lower() in nvidia_names:
                    continue
                vram_bytes = item.get("AdapterRAM") or 0
                capped = vram_bytes == 4294967296
                other.append(GPUInfo(
                    name=name,
                    vram_gb=round(vram_bytes / (1024 ** 3), 1),
                    vendor=_detect_vendor(name),
                    vram_capped=capped,
                ))
    except Exception:
        pass
    return nvidia + other


def _get_storage_info() -> StorageInfo:
    try:
        import psutil
        best = None
        for part in psutil.disk_partitions(all=False):
            if not part.mountpoint:
                continue
            try:
                u = psutil.disk_usage(part.mountpoint)
                if best is None or u.free > best[0]:
                    best = (u.free, u.total, part.mountpoint)
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
    try:
        import psutil
        u = psutil.disk_usage("C:\\")
        return StorageInfo(round(u.free/(1024**3),1), round(u.total/(1024**3),1), "C:\\")
    except Exception:
        pass
    return StorageInfo(0.0, 0.0, "Unknown")


def _get_cpu_info() -> CPUInfo:
    try:
        import psutil
        import cpuinfo
        info = cpuinfo.get_cpu_info()
        freq = psutil.cpu_freq()
        name = info.get("brand_raw") or platform.processor() or "Unknown CPU"
        arch = info.get("arch", platform.machine())
        max_freq = round(
            (freq.max if freq and freq.max else (freq.current if freq else 0)) / 1000, 2
        )
        is_apple = any(k in name for k in ("Apple", "M1", "M2", "M3", "M4"))
        return CPUInfo(
            name=name,
            physical_cores=psutil.cpu_count(logical=False) or 1,
            logical_cores=psutil.cpu_count(logical=True) or 1,
            max_freq_ghz=max_freq,
            architecture=arch,
            is_apple_silicon=is_apple,
        )
    except Exception:
        return CPUInfo(platform.processor() or "Unknown CPU", 1, 1, 0.0, platform.machine())


def _get_ram_info() -> RAMInfo:
    try:
        import psutil
        mem = psutil.virtual_memory()
        return RAMInfo(
            total_gb=round(mem.total / (1024 ** 3), 1),
            available_gb=round(mem.available / (1024 ** 3), 1),
        )
    except Exception:
        return RAMInfo(0.0, 0.0)


def scan_hardware() -> SystemInfo:
    os_name = platform.system()
    gpus = _get_gpus_windows() if os_name == "Windows" else _get_nvidia_gpus()
    seen, unique = set(), []
    for g in gpus:
        if g.name not in seen:
            seen.add(g.name)
            unique.append(g)
    return SystemInfo(
        cpu=_get_cpu_info(),
        ram=_get_ram_info(),
        gpus=unique,
        storage=_get_storage_info(),
        os_name=os_name,
        os_version=platform.version(),
    )
