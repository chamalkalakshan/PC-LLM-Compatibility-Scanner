import platform
from dataclasses import dataclass


@dataclass
class CPUInfo:
    name: str
    physical_cores: int
    logical_cores: int
    max_freq_ghz: float
    architecture: str


@dataclass
class RAMInfo:
    total_gb: float
    available_gb: float


@dataclass
class SystemInfo:
    cpu: CPUInfo
    ram: RAMInfo
    os_name: str
    os_version: str


def _get_cpu_info() -> CPUInfo:
    try:
        import psutil
        freq = psutil.cpu_freq()
        max_freq = round(
            (freq.max if freq and freq.max else (freq.current if freq else 0)) / 1000, 2
        )
        return CPUInfo(
            name=platform.processor() or "Unknown CPU",
            physical_cores=psutil.cpu_count(logical=False) or 1,
            logical_cores=psutil.cpu_count(logical=True) or 1,
            max_freq_ghz=max_freq,
            architecture=platform.machine(),
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
    return SystemInfo(
        cpu=_get_cpu_info(),
        ram=_get_ram_info(),
        os_name=platform.system(),
        os_version=platform.version(),
    )
