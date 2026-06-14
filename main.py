#!/usr/bin/env python3
"""PC LLM Compatibility Scanner - Author: Chamalka Lakshan"""

import argparse
import sys

from scanner.hardware import scan_hardware
from scanner.recommender import get_recommendations
from scanner.display import console, print_banner, print_hardware, print_recommendations


def main():
    parser = argparse.ArgumentParser(prog="llm-scanner",
        description="Scan PC hardware and get local LLM recommendations.")
    parser.add_argument("--top", type=int, default=0, metavar="N",
        help="Show only the top N recommended models")
    parser.add_argument("--tier", type=str, default=None,
        choices=["EXCELLENT", "GOOD", "POSSIBLE", "SLOW", "NO-GO"])
    parser.add_argument("--hide-nogo", action="store_true",
        help="Hide models that cannot run on your hardware")
    args = parser.parse_args()

    print_banner()
    console.print("[dim]Scanning hardware...[/dim]")
    try:
        hw = scan_hardware()
    except Exception as e:
        console.print(f"[red]Hardware scan failed: {e}[/red]")
        sys.exit(1)

    print_hardware(hw)
    recs = get_recommendations(hw)
    show_no_go = not args.hide_nogo
    print_recommendations(recs, show_no_go=show_no_go, filter_tier=args.tier)


if __name__ == "__main__":
    main()
