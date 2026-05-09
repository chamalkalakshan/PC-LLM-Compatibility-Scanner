import platform
import subprocess
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


@dataclass
class SystemInfo:
    cpu: CPUInfo
    ram: RAMInfo
    gpus: List[GPUInfo]
    os_name: str
    os_version: str


def _detect_vendor(name: str) -> str:
    n = name.lower()
    if any(k in n for k in ["nvidia", "geforce", "rtx", "gtx", "quadro"]):
        return "NVIDIA"
    if any(k in n for k in ["amd", "radeon", "rx ", "vega"]):
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
                    name = parts[0].strip()
                    vram_gb = round(float(parts[1].strip()) / 1024, 1)
                    gpus.append(GPUInfo(name=name, vram_gb=vram_gb, vendor="NVIDIA"))
            return gpus
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass
    return []


def _get_cpu_info() -> CPUInfo:
    try:
        import psutil
        freq = psutil.cpu_freq()
        max_freq = round(
            (freq.max if freq and freq.max else (freq.current if freq else 0)) / 1000, 2
        )
        name = platform.processor() or "Unknown CPU"
        return CPUInfo(
            name=name,
            physical_cores=psutil.cpu_count(logical=False) or 1,
            logical_cores=psutil.cpu_count(logical=True) or 1,
            max_freq_ghz=max_freq,
            architecture=platform.machine(),
            is_apple_silicon="Apple" in name,
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
    gpus = _get_nvidia_gpus()
    return SystemInfo(
        cpu=_get_cpu_info(),
        ram=_get_ram_info(),
        gpus=gpus,
        os_name=platform.system(),
        os_version=platform.version(),
    )
