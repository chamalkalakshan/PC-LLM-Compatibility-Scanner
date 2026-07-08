from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text
from rich.rule import Rule
from rich.align import Align

from .hardware import SystemInfo
from .recommender import Recommendation, RunTier, TIER_EMOJI, TIER_LABEL, get_summary_stats

console = Console(force_terminal=True, highlight=False)

TIER_STYLE = {
    RunTier.EXCELLENT: "bold green",
    RunTier.GOOD:      "green",
    RunTier.POSSIBLE:  "yellow",
    RunTier.SLOW:      "dark_orange",
    RunTier.NO_GO:     "red",
}


def _bar(value: float, maximum: float, width: int = 20) -> str:
    filled = min(int((value / maximum) * width) if maximum > 0 else 0, width)
    return "#" * filled + "-" * (width - filled)


def print_banner():
    console.print()
    console.print(Panel(
        Align.center(
            "[bold cyan]PC LLM Compatibility Scanner[/bold cyan]\n"
            "[dim]Detect your hardware · Match local LLMs · Run them smoothly[/dim]"
        ),
        border_style="cyan",
        padding=(1, 4),
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
            vendor_color = {"NVIDIA": "green", "AMD": "red", "Intel": "blue", "Apple": "white"}.get(gpu.vendor, "white")
            console.print(f"  [bold]GPU {i}[/bold]  [{vendor_color}]{gpu.name}[/{vendor_color}]")
            if gpu.vram_gb > 0:
                cap_note = "  [yellow](WMI 32-bit cap – actual may be higher)[/yellow]" if gpu.vram_capped else ""
                console.print(f"         VRAM: [cyan]{gpu.vram_gb:.1f} GB[/cyan]{cap_note}")
            elif gpu.vram_unknown:
                console.print("         VRAM: [yellow]Unknown (install vendor tools, e.g. rocm-smi, for size)[/yellow]")
            else:
                console.print("         VRAM: [dim]Not detected (integrated / unknown)[/dim]")
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


def print_recommendations(recs: List[Recommendation], show_no_go: bool = True, filter_tier: Optional[str] = None):
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

    table = Table(
        show_header=True,
        header_style="bold white on #1a1a2e",
        border_style="dim cyan",
        box=box.ROUNDED,
        expand=True,
        leading=0,
    )
    table.add_column("",         width=2,  no_wrap=True)
    table.add_column("Model",    min_width=22, no_wrap=True)
    table.add_column("Params",   width=7,  no_wrap=True, justify="right")
    table.add_column("Status",   min_width=10, no_wrap=True)
    table.add_column("Mode",     width=14, no_wrap=True)
    table.add_column("VRAM req", width=9,  no_wrap=True, justify="right")
    table.add_column("RAM req",  width=8,  no_wrap=True, justify="right")
    table.add_column("Use Cases",min_width=24)
    table.add_column("Ollama",   min_width=22)

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
        if len(rec.model.use_cases) > 3:
            use_str += f" +{len(rec.model.use_cases)-3}"

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


def print_detail(rec: Recommendation):
    style = TIER_STYLE[rec.tier]
    emoji = TIER_EMOJI[rec.tier]

    lines = [
        f"[bold]{rec.model.name}[/bold]  [dim]({rec.model.parameters_b:.0f}B params)[/dim]",
        f"  {rec.model.description}",
        "",
        f"  Status : [{style}]{emoji} {rec.tier.value}[/{style}]",
        f"  Mode   : {rec.run_mode}",
        f"  VRAM   : min {rec.model.min_vram_gb:.0f} GB  /  recommended {rec.model.rec_vram_gb:.0f} GB",
        f"  RAM    : min {rec.model.min_ram_gb:.0f} GB  /  recommended {rec.model.rec_ram_gb:.0f} GB",
        f"  Context: {rec.model.context_length:,} tokens",
        f"  Ollama : [cyan]{rec.ollama_cmd}[/cyan]",
    ]
    if rec.notes:
        lines.append("")
        lines.append("  Notes:")
        for n in rec.notes:
            lines.append(f"    · {n}")

    console.print(Panel("\n".join(lines), border_style=style, padding=(0, 1)))


def print_top_picks(recs: List[Recommendation], n: int = 5):
    console.print(Rule(f"[bold cyan]Top {n} Picks for Your Hardware[/bold cyan]", style="cyan"))
    console.print()
    runnable = [r for r in recs if r.tier != RunTier.NO_GO][:n]
    for i, rec in enumerate(runnable, 1):
        style = TIER_STYLE[rec.tier]
        emoji = TIER_EMOJI[rec.tier]
        console.print(
            f"  [bold]{i}.[/bold] {emoji} [{style}]{rec.model.name}[/{style}]"
            f"  [dim]({rec.model.parameters_b:.0f}B · {rec.run_mode})[/dim]"
        )
        console.print(f"     [dim]{rec.model.description}[/dim]")
        console.print(f"     [cyan]{rec.ollama_cmd}[/cyan]")
        if rec.notes:
            console.print(f"     [dim]{rec.notes[0]}[/dim]")
        console.print()


def print_legend():
    console.print(Rule("[dim]Legend[/dim]", style="dim"))
    for tier, emoji in TIER_EMOJI.items():
        style = TIER_STYLE[tier]
        console.print(f"  {emoji} [{style}]{tier.value:10}[/{style}]  {TIER_LABEL[tier]}")
    console.print()
