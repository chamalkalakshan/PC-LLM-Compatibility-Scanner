from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.align import Align

from .hardware import SystemInfo

console = Console(force_terminal=True, highlight=False)


def _bar(value, maximum, width=20):
    filled = min(int((value / maximum) * width) if maximum > 0 else 0, width)
    return "#" * filled + "-" * (width - filled)


def print_banner():
    console.print()
    console.print(Panel(
        Align.center(
            "[bold cyan]PC LLM Compatibility Scanner[/bold cyan]\n"
            "[dim]Detect your hardware · Match local LLMs · Run them smoothly[/dim]"
        ),
        border_style="cyan", padding=(1, 4),
    ))
    console.print()


def print_hardware(hw: SystemInfo):
    console.print(Rule("[bold cyan]System Hardware[/bold cyan]", style="cyan"))
    console.print()
    cpu = hw.cpu
    console.print(f"  [bold]CPU[/bold]   [cyan]{cpu.name}[/cyan]")
    console.print(f"         {cpu.physical_cores} physical · {cpu.logical_cores} logical · {cpu.max_freq_ghz:.2f} GHz · {cpu.architecture}")
    console.print()
    ram = hw.ram
    used_gb = ram.total_gb - ram.available_gb
    bar = _bar(used_gb, ram.total_gb)
    console.print(f"  [bold]RAM[/bold]   [cyan]{ram.total_gb:.1f} GB total[/cyan]  ·  {ram.available_gb:.1f} GB free")
    console.print(f"         [{bar}] {used_gb:.1f} GB used")
    console.print()
    if hw.gpus:
        for i, gpu in enumerate(hw.gpus, 1):
            console.print(f"  [bold]GPU {i}[/bold]  [green]{gpu.name}[/green]")
            if gpu.vram_gb > 0:
                console.print(f"         VRAM: [cyan]{gpu.vram_gb:.1f} GB[/cyan]")
    else:
        console.print("  [bold]GPU[/bold]   [dim]None detected[/dim]")
    console.print()
    console.print(f"  [bold]OS[/bold]    {hw.os_name}  {hw.os_version[:60]}")
    console.print()
