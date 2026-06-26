#!/usr/bin/env python3
"""
PC LLM Compatibility Scanner — Textual TUI
Author: Chamalka Lakshan
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Footer, Header, Label, Static
from textual.worker import Worker
from textual import on, work
from rich.text import Text

from scanner.hardware import scan_hardware, SystemInfo
from scanner.recommender import (
    Recommendation,
    RunTier,
    TIER_EMOJI,
    get_recommendations,
    get_summary_stats,
)

# ── Helpers ─────────────────────────────────────────────────────────────────

TIER_COLOR = {
    RunTier.EXCELLENT: "bold green",
    RunTier.GOOD:      "green",
    RunTier.POSSIBLE:  "yellow",
    RunTier.SLOW:      "dark_orange",
    RunTier.NO_GO:     "red",
}

FILTER_OPTIONS = [
    ("all",       "All"),
    ("EXCELLENT", "🚀 Excellent"),
    ("GOOD",      "✅ Good"),
    ("POSSIBLE",  "⚡ Possible"),
    ("SLOW",      "🐌 Slow"),
    ("NO-GO",     "❌ No-Go"),
]


def _bar(value: float, maximum: float, width: int = 14) -> str:
    filled = min(int((value / maximum) * width) if maximum > 0 else 0, width)
    return "█" * filled + "░" * (width - filled)


# ── Model Detail Modal ───────────────────────────────────────────────────────

class ModelDetailScreen(ModalScreen):
    """Popup showing full details for a selected LLM."""

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q",      "dismiss", "Close"),
    ]

    def __init__(self, rec: Recommendation) -> None:
        super().__init__()
        self.rec = rec

    def compose(self) -> ComposeResult:
        r = self.rec
        m = r.model
        tc = TIER_COLOR[r.tier]
        emoji = TIER_EMOJI[r.tier]

        body = "\n".join([
            f"[bold]{m.name}[/bold]  [dim]{m.parameters_b:.0f}B · {m.family} · {m.released_year}[/dim]",
            f"[dim]{m.description}[/dim]",
            "",
            f"  Tier      [{tc}]{emoji}  {r.tier.value}[/{tc}]",
            f"  Mode      {r.run_mode}",
            f"  VRAM      min [cyan]{m.min_vram_gb:.0f} GB[/cyan]  ·  rec [cyan]{m.rec_vram_gb:.0f} GB[/cyan]",
            f"  RAM       min [cyan]{m.min_ram_gb:.0f} GB[/cyan]  ·  rec [cyan]{m.rec_ram_gb:.0f} GB[/cyan]",
            f"  Context   {m.context_length:,} tokens",
            f"  Use for   [dim]{', '.join(m.use_cases)}[/dim]",
            "",
            f"  [bold cyan]$ {r.ollama_cmd}[/bold cyan]",
            *(["", "  Notes:"] + [f"    • {n}" for n in r.notes] if r.notes else []),
        ])

        with Container(id="modal-box"):
            yield Static(body, id="modal-body")
            yield Button("Close  [Esc]", id="modal-close", variant="primary")

    @on(Button.Pressed, "#modal-close")
    def _close(self) -> None:
        self.dismiss()


# ── Hardware Panel ───────────────────────────────────────────────────────────

class HardwarePanel(Static):
    """Left-side panel that renders live hardware info."""

    def _build_display(self, hw: SystemInfo | None, scanning: bool) -> str:
        if scanning:
            return "\n\n  [dim]Scanning hardware…[/dim]"
        if hw is None:
            return "\n\n  [red]No hardware data.[/red]"

        cpu = hw.cpu
        ram = hw.ram
        ram_used = ram.total_gb - ram.available_gb
        ram_pct = int((ram_used / ram.total_gb) * 100) if ram.total_gb > 0 else 0
        ram_col = "green" if ram_pct < 70 else "yellow" if ram_pct < 90 else "red"

        lines = [
            " [bold cyan]CPU[/bold cyan]",
            f"  {cpu.name}",
            f"  [dim]{cpu.physical_cores}c · {cpu.logical_cores}t · {cpu.max_freq_ghz:.1f} GHz[/dim]",
            "",
            " [bold cyan]RAM[/bold cyan]",
            f"  {ram.total_gb:.1f} GB  [dim]({ram.available_gb:.1f} GB free)[/dim]",
            f"  [{ram_col}]{_bar(ram_used, ram.total_gb)}[/]  {ram_pct}%",
            "",
        ]

        if hw.gpus:
            lines.append(" [bold cyan]GPU[/bold cyan]")
            for gpu in hw.gpus:
                vc = {"NVIDIA": "green", "AMD": "red", "Intel": "blue"}.get(gpu.vendor, "white")
                lines.append(f"  [{vc}]{gpu.name}[/{vc}]")
                if gpu.vram_gb > 0:
                    cap = " [yellow](cap)[/yellow]" if gpu.vram_capped else ""
                    vram_bar = _bar(gpu.vram_gb, max(gpu.vram_gb * 1.1, 24))
                    lines.append(f"  {gpu.vram_gb:.1f} GB VRAM{cap}")
                    lines.append(f"  [green]{vram_bar}[/]")
            lines.append("")
        else:
            lines += [" [bold cyan]GPU[/bold cyan]", "  [dim]None detected[/dim]", ""]

        st = hw.storage
        if st.total_gb > 0:
            disk_used = st.total_gb - st.free_gb
            disk_pct = int((disk_used / st.total_gb) * 100)
            disk_col = "green" if disk_pct < 80 else "yellow" if disk_pct < 95 else "red"
            lines += [
                " [bold cyan]Disk[/bold cyan]",
                f"  {st.drive}  [cyan]{st.free_gb:.0f} GB free[/cyan]",
                f"  [{disk_col}]{_bar(disk_used, st.total_gb)}[/]  {disk_pct}%",
                "",
            ]

        lines.append(f" [dim]{hw.os_name}[/dim]")
        return "\n".join(lines)

    def refresh_content(self, hw: SystemInfo | None, scanning: bool) -> None:
        self.update(self._build_display(hw, scanning))


# ── Main App ─────────────────────────────────────────────────────────────────

class LLMScannerApp(App):
    """PC LLM Compatibility Scanner — Textual TUI."""

    TITLE = "PC LLM Compatibility Scanner"
    SUB_TITLE = "by Chamalka Lakshan"

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 34 1fr;
        background: $background;
    }

    /* ── Left panel ─────────────── */
    #left {
        height: 100%;
        layout: vertical;
        border: solid cyan;
        padding: 1 1;
    }

    #hw-panel {
        height: 1fr;
    }

    #action-row {
        height: 3;
        layout: horizontal;
        margin-top: 1;
    }

    #action-row Button {
        width: 1fr;
        margin: 0 1;
    }

    /* ── Right panel ────────────── */
    #right {
        height: 100%;
        layout: vertical;
    }

    #filter-row {
        height: 3;
        layout: horizontal;
        background: $surface;
        padding: 0 1;
    }

    #filter-row Button {
        min-width: 14;
        margin: 0 0;
        height: 3;
        border: none;
        background: $panel;
        color: $text-muted;
    }

    #filter-row Button:hover {
        background: $surface-lighten-1;
        color: $text;
    }

    #filter-row Button.active {
        background: cyan;
        color: $background;
        text-style: bold;
    }

    #model-table {
        height: 1fr;
    }

    #status {
        height: 1;
        background: $surface;
        color: $text-muted;
        padding: 0 2;
    }

    /* ── Modal ──────────────────── */
    ModelDetailScreen {
        align: center middle;
    }

    #modal-box {
        width: 72;
        height: auto;
        max-height: 38;
        border: double cyan;
        background: $surface;
        padding: 1 2;
    }

    #modal-body {
        margin-bottom: 1;
    }

    #modal-close {
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("q", "quit",   "Quit"),
        Binding("r", "rescan", "Rescan"),
        Binding("e", "export", "Export JSON"),
        Binding("f", "focus_filter", "Filter", show=False),
    ]

    # ── State ──────────────────────────────────────────────────────────────
    _hw:     SystemInfo | None       = None
    _recs:   list[Recommendation]    = []
    _filter: str                     = "all"

    # ── Layout ─────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header()

        # Left
        with Vertical(id="left"):
            yield HardwarePanel("", id="hw-panel")
            with Horizontal(id="action-row"):
                yield Button("⟳  Rescan", id="btn-rescan", variant="primary")
                yield Button("⬇  Export", id="btn-export", variant="default")

        # Right
        with Vertical(id="right"):
            with Horizontal(id="filter-row"):
                for key, label in FILTER_OPTIONS:
                    cls = "active" if key == "all" else ""
                    yield Button(label, id=f"f-{key}", classes=cls)
            yield DataTable(id="model-table", cursor_type="row", zebra_stripes=True)
            yield Static("", id="status")

        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#model-table", DataTable)
        table.add_column("",       width=2,  key="ico")
        table.add_column("Model",  width=24, key="name")
        table.add_column("Params", width=7,  key="params")
        table.add_column("Tier",   width=10, key="tier")
        table.add_column("Mode",   width=13, key="mode")
        table.add_column("VRAM",   width=6,  key="vram")
        table.add_column("RAM",    width=6,  key="ram")
        table.add_column("Ollama command", width=28, key="ollama")
        self.action_rescan()

    # ── Scan worker ────────────────────────────────────────────────────────

    @work(exclusive=True, thread=True)
    def action_rescan(self) -> None:
        self.call_from_thread(self._set_scanning, True)
        try:
            hw   = scan_hardware()
            recs = get_recommendations(hw)
            self.call_from_thread(self._apply, hw, recs)
        except Exception as exc:
            self.call_from_thread(self.notify, f"Scan failed: {exc}", severity="error")
        finally:
            self.call_from_thread(self._set_scanning, False)

    def _set_scanning(self, state: bool) -> None:
        panel = self.query_one("#hw-panel", HardwarePanel)
        panel.refresh_content(self._hw, state)
        btn = self.query_one("#btn-rescan", Button)
        btn.disabled = state
        btn.label = "Scanning…" if state else "⟳  Rescan"

    def _apply(self, hw: SystemInfo, recs: list[Recommendation]) -> None:
        self._hw   = hw
        self._recs = recs
        self.query_one("#hw-panel", HardwarePanel).refresh_content(hw, False)
        self._rebuild_table()

    # ── Table ──────────────────────────────────────────────────────────────

    def _rebuild_table(self) -> None:
        table = self.query_one("#model-table", DataTable)
        table.clear()

        visible = [
            r for r in self._recs
            if self._filter == "all" or r.tier.value == self._filter
        ]

        for rec in visible:
            tc = TIER_COLOR[rec.tier]
            table.add_row(
                TIER_EMOJI[rec.tier],
                Text(rec.model.name, style=tc),
                Text(f"{rec.model.parameters_b:.0f}B", style="dim"),
                Text(rec.tier.value, style=tc),
                Text(rec.run_mode, style="dim"),
                Text(f"{rec.model.min_vram_gb:.0f}GB", style="dim"),
                Text(f"{rec.model.min_ram_gb:.0f}GB", style="dim"),
                Text(rec.ollama_cmd, style="cyan"),
                key=rec.model.name,
            )

        if self._recs:
            s = get_summary_stats(self._recs)
            self.query_one("#status", Static).update(
                f"  {s['total']} models · "
                f"[green]{s['excellent_good']}[/green] excellent/good · "
                f"[bold]{s['runnable']}[/bold] runnable · "
                f"[red]{s['by_tier']['NO-GO']}[/red] insufficient"
                + (f"  [dim]({len(visible)} shown)[/dim]" if self._filter != "all" else "")
            )

    # ── Events ─────────────────────────────────────────────────────────────

    @on(Button.Pressed)
    def _any_button(self, event: Button.Pressed) -> None:
        if not event.button.id or not event.button.id.startswith("f-"):
            return
        for key, _ in FILTER_OPTIONS:
            self.query_one(f"#f-{key}", Button).remove_class("active")
        event.button.add_class("active")
        self._filter = event.button.id[2:]  # strip "f-" prefix
        self._rebuild_table()

    @on(Button.Pressed, "#btn-rescan")
    def _btn_rescan(self) -> None:
        self.action_rescan()

    @on(Button.Pressed, "#btn-export")
    def action_export(self) -> None:
        if not self._hw or not self._recs:
            self.notify("Run a scan first.", severity="warning")
            return
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = Path(f"scan_results_{ts}.json")
        data = {
            "scanned_at": ts,
            "hardware": {
                "cpu":        self._hw.cpu.name,
                "ram_total_gb": self._hw.ram.total_gb,
                "gpus": [{"name": g.name, "vram_gb": g.vram_gb} for g in self._hw.gpus],
                "disk_free_gb": self._hw.storage.free_gb,
            },
            "recommendations": [
                {
                    "model":      r.model.name,
                    "family":     r.model.family,
                    "parameters": r.model.parameters_b,
                    "tier":       r.tier.value,
                    "run_mode":   r.run_mode,
                    "ollama_cmd": r.ollama_cmd,
                    "notes":      r.notes,
                }
                for r in self._recs
            ],
        }
        path.write_text(json.dumps(data, indent=2))
        self.notify(f"Saved → {path}", severity="information")

    @on(DataTable.RowSelected, "#model-table")
    def _row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key is None:
            return
        name = str(event.row_key.value)
        for rec in self._recs:
            if rec.model.name == name:
                self.push_screen(ModelDetailScreen(rec))
                return

    def action_focus_filter(self) -> None:
        self.query_one("#f-all", Button).focus()


# ── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    LLMScannerApp().run()


if __name__ == "__main__":
    main()
