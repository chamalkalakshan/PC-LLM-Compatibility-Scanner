#!/usr/bin/env python3
"""PC LLM Compatibility Scanner - Author: Chamalka Lakshan"""

from scanner.hardware import scan_hardware
from scanner.recommender import get_recommendations, RunTier
from scanner.display import console, print_banner, print_hardware

TIER_EMOJI = {"EXCELLENT": "🚀", "GOOD": "✅", "POSSIBLE": "⚡", "SLOW": "🐌", "NO-GO": "❌"}


def main():
    print_banner()
    console.print("[dim]Scanning hardware...[/dim]")
    hw = scan_hardware()
    print_hardware(hw)

    recs = get_recommendations(hw)
    console.print("\n[bold cyan]LLM Compatibility:[/bold cyan]\n")
    for r in recs:
        emoji = TIER_EMOJI.get(r.tier.value, "?")
        console.print(
            f"  {emoji} [{r.tier.value:10}]  {r.model.name:<28} "
            f"[dim]{r.model.parameters_b:.0f}B  {r.run_mode}[/dim]"
        )
        for n in r.notes:
            console.print(f"             [dim]{n}[/dim]")


if __name__ == "__main__":
    main()
