from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.rule import Rule
from rich.align import Align

from .hardware import SystemInfo
from .recommender import Recommendation, RunTier, get_summary_stats

console = Console(force_terminal=True, highlight=False)

TIER_STYLE = {
    RunTier.EXCELLENT: "bold green",
    RunTier.GOOD:      "green",
    RunTier.POSSIBLE:  "yellow",
    RunTier.SLOW:      "dark_orange",
    RunTier.NO_GO:     "red",
}
TIER_EMOJI = {
    RunTier.EXCELLENT: "🚀",
    RunTier.GOOD:      "✅",
    RunTier.POSSIBLE:  "⚡",
    RunTier.SLOW:      "🐌",
    RunTier.NO_GO:     "❌",
}
TIER_LABEL = {
    RunTier.EXCELLENT: "Excellent - GPU, fast",
    RunTier.GOOD:      "Good - GPU fits",
    RunTier.POSSIBLE:  "Possible - partial offload / CPU",
    RunTier.SLOW:      "Slow - CPU only",
    RunTier.NO_GO:     "Insufficient hardware",
}


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
    console.print(f"         {cpu.physical_cores} physical cores · {cpu.logical_cores} logical · {cpu.max_freq_ghz:.2f} GHz · {cpu.architecture}")
    if cpu.is_apple_silicon:
        console.print("         [green]Apple Silicon: unified memory (RAM = VRAM)[/green]")
    console.print()
    ram = hw.ram
    used_gb = ram.total_gb - ram.available_gb
    bar = _bar(used_gb, ram.total_gb)
    console.print(f"  [bold]RAM[/bold]   [cyan]{ram.total_gb:.1f} GB total[/cyan]  ·  {ram.available_gb:.1f} GB free")
    console.print(f"         [{bar}] {used_gb:.1f} GB used")
    console.print()
    if hw.gpus:
        for i, gpu in enumerate(hw.gpus, 1):
            vc = {"NVIDIA": "green", "AMD": "red", "Intel": "blue"}.get(gpu.vendor, "white")
            console.print(f"  [bold]GPU {i}[/bold]  [{vc}]{gpu.name}[/{vc}]")
            if gpu.vram_gb > 0:
                cap = "  [yellow](WMI 32-bit cap)[/yellow]" if gpu.vram_capped else ""
                console.print(f"         VRAM: [cyan]{gpu.vram_gb:.1f} GB[/cyan]{cap}")
            else:
                console.print("         VRAM: [dim]Not detected[/dim]")
    else:
        console.print("  [bold]GPU[/bold]   [dim]None detected[/dim]")
    console.print()
    st = hw.storage
    bar = _bar(st.total_gb - st.free_gb, st.total_gb)
    console.print(f"  [bold]Disk[/bold]  {st.drive}  ·  [cyan]{st.free_gb:.0f} GB free[/cyan] of {st.total_gb:.0f} GB")
    console.print(f"         [{bar}] {st.total_gb - st.free_gb:.0f} GB used")
    console.print()
    console.print(f"  [bold]OS[/bold]    {hw.os_name}  {hw.os_version[:60]}")
    console.print()


def print_recommendations(recs: List[Recommendation], show_no_go=True, filter_tier=None):
    console.print(Rule("[bold cyan]LLM Compatibility Report[/bold cyan]", style="cyan"))
    console.print()
    stats = get_summary_stats(recs)
    console.print(
        f"  [dim]Analysed[/dim] [bold]{stats['total']}[/bold] [dim]models  ·  "
        f"[/dim][bold green]{stats['excellent_good']}[/bold green][dim] excellent/good  ·  "
        f"[/dim][bold]{stats['runnable']}[/bold][dim] runnable  ·  "
        f"[/dim][bold red]{stats['by_tier']['NO-GO']}[/bold red][dim] insufficient[/dim]"
    )
    console.print()
    table = Table(show_header=True, header_style="bold white on #1a1a2e",
                  border_style="dim cyan", box=box.ROUNDED, expand=True)
    table.add_column("", width=2, no_wrap=True)
    table.add_column("Model", min_width=22, no_wrap=True)
    table.add_column("Params", width=7, no_wrap=True, justify="right")
    table.add_column("Status", min_width=10, no_wrap=True)
    table.add_column("Mode", width=14, no_wrap=True)
    table.add_column("VRAM req", width=9, no_wrap=True, justify="right")
    table.add_column("RAM req", width=8, no_wrap=True, justify="right")
    table.add_column("Use Cases", min_width=24)
    table.add_column("Ollama", min_width=22)
    last_tier = None
    for rec in recs:
        if not show_no_go and rec.tier == RunTier.NO_GO:
            continue
        if filter_tier and rec.tier.value != filter_tier.upper():
            continue
        style = TIER_STYLE[rec.tier]
        emoji = TIER_EMOJI[rec.tier]
        if rec.tier != last_tier:
            if last_tier is not None:
                table.add_section()
            last_tier = rec.tier
        use_str = ", ".join(rec.model.use_cases[:3])
        table.add_row(
            emoji,
            f"[{style}]{rec.model.name}[/{style}]",
            f"[dim]{rec.model.parameters_b:.0f}B[/dim]",
            f"[{style}]{rec.tier.value}[/{style}]",
            f"[dim]{rec.run_mode}[/dim]",
            f"[dim]{rec.model.min_vram_gb:.0f} GB[/dim]",
            f"[dim]{rec.model.min_ram_gb:.0f} GB[/dim]",
            f"[dim]{use_str}[/dim]",
            f"[cyan]{rec.ollama_cmd}[/cyan]",
        )
    console.print(table)
    console.print()
