#!/usr/bin/env python3
"""
PC LLM Compatibility Scanner
Author: Chamalka Lakshan
"""

import argparse
import json
import sys
from pathlib import Path

from scanner.hardware import scan_hardware
from scanner.recommender import get_recommendations, RunTier
from scanner.display import (
    console,
    print_banner,
    print_hardware,
    print_recommendations,
    print_top_picks,
    print_legend,
    print_detail,
)


def export_json(hw, recs, output_path: str):
    data = {
        "hardware": {
            "cpu": {
                "name": hw.cpu.name,
                "physical_cores": hw.cpu.physical_cores,
                "logical_cores": hw.cpu.logical_cores,
                "max_freq_ghz": hw.cpu.max_freq_ghz,
                "architecture": hw.cpu.architecture,
            },
            "ram_total_gb": hw.ram.total_gb,
            "ram_available_gb": hw.ram.available_gb,
            "gpus": [
                {"name": g.name, "vram_gb": g.vram_gb, "vendor": g.vendor}
                for g in hw.gpus
            ],
            "storage_free_gb": hw.storage.free_gb,
            "os": hw.os_name,
        },
        "recommendations": [
            {
                "model": r.model.name,
                "family": r.model.family,
                "parameters_b": r.model.parameters_b,
                "tier": r.tier.value,
                "run_mode": r.run_mode,
                "notes": r.notes,
                "ollama_cmd": r.ollama_cmd,
                "use_cases": r.model.use_cases,
            }
            for r in recs
        ],
    }
    Path(output_path).write_text(json.dumps(data, indent=2))
    console.print(f"[green]Results saved to[/green] [cyan]{output_path}[/cyan]")


def main():
    parser = argparse.ArgumentParser(
        prog="llm-scanner",
        description="Scan PC hardware and get local LLM recommendations.",
    )
    parser.add_argument(
        "--top", type=int, default=0, metavar="N",
        help="Show only the top N recommended models (default: show all)",
    )
    parser.add_argument(
        "--tier", type=str, default=None,
        choices=["EXCELLENT", "GOOD", "POSSIBLE", "SLOW", "NO-GO"],
        help="Filter output to a specific compatibility tier",
    )
    parser.add_argument(
        "--hide-nogo", action="store_true",
        help="Hide models that cannot run on your hardware",
    )
    parser.add_argument(
        "--detail", type=str, default=None, metavar="MODEL_NAME",
        help='Show detailed breakdown for a specific model (e.g. "Llama 3.1 8B")',
    )
    parser.add_argument(
        "--export-json", type=str, default=None, metavar="FILE",
        help="Export results to a JSON file",
    )
    parser.add_argument(
        "--no-banner", action="store_true",
        help="Skip the banner (useful for scripting)",
    )
    args = parser.parse_args()

    if not args.no_banner:
        print_banner()

    # Scan hardware
    console.print("[dim]Scanning hardware...[/dim]")
    try:
        hw = scan_hardware()
    except Exception as e:
        console.print(f"[red]Hardware scan failed: {e}[/red]")
        sys.exit(1)

    print_hardware(hw)

    # Generate recommendations
    recs = get_recommendations(hw)

    if args.detail:
        query = args.detail.lower()
        matches = [r for r in recs if query in r.model.name.lower()]
        if not matches:
            console.print(f"[red]No model found matching '{args.detail}'[/red]")
            console.print("[dim]Available models:[/dim]")
            for r in recs:
                console.print(f"  {r.model.name}")
            sys.exit(1)
        for m in matches:
            print_detail(m)
        return

    if args.top and args.top > 0:
        print_top_picks(recs, n=args.top)
    else:
        show_no_go = not args.hide_nogo
        print_recommendations(recs, show_no_go=show_no_go, filter_tier=args.tier)
        print_top_picks(recs, n=5)

    print_legend()

    if args.export_json:
        export_json(hw, recs, args.export_json)


if __name__ == "__main__":
    main()
