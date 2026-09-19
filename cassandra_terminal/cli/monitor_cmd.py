from __future__ import annotations

import time

import typer
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table

from cassandra_terminal.modules.monitor import SystemSnapshot, get_system_snapshot
from cassandra_terminal.ui.theme import PALETTE, get_theme_header

app = typer.Typer(
    name="monitor",
    help="📊 Real-time system resource monitor (CPU, RAM, Disk, Top Processes)",
    no_args_is_help=False,
)
console = Console()


def render_monitor_view(snapshot: SystemSnapshot) -> Layout:
    """Construct Rich layout containing system metrics and process table."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="metrics", size=9),
        Layout(name="processes"),
    )

    # 1. Header
    layout["header"].update(
        Panel(
            f"[bold {PALETTE['cyan']}]⚡ CASSANDRA SYSTEM MONITOR[/bold {PALETTE['cyan']}] "
            f"[dim]| Cores: {snapshot.cpu_count_physical}P/{snapshot.cpu_count_logical}L[/dim]",
            border_style=PALETTE["blue"],
        )
    )

    # 2. Metrics Table / Columns
    metrics_table = Table.grid(expand=True, padding=(0, 2))
    metrics_table.add_column(ratio=1)
    metrics_table.add_column(ratio=1)
    metrics_table.add_column(ratio=1)

    # CPU Panel
    cpu_bar = ProgressBar(total=100, completed=snapshot.cpu_percent, width=18)
    cpu_color = (
        PALETTE["green"]
        if snapshot.cpu_percent < 60
        else PALETTE["yellow"]
        if snapshot.cpu_percent < 85
        else PALETTE["magenta"]
    )
    cpu_panel = Panel(
        Group(
            f"[bold {cpu_color}]{snapshot.cpu_percent}%[/bold {cpu_color}]",
            cpu_bar,
        ),
        title="[bold]CPU Load[/bold]",
        subtitle=f"{snapshot.cpu_count_logical} Threads",
        border_style=cpu_color,
    )

    # RAM Panel
    ram_bar = ProgressBar(total=100, completed=snapshot.ram_percent, width=18)
    ram_color = (
        PALETTE["green"]
        if snapshot.ram_percent < 70
        else PALETTE["yellow"]
        if snapshot.ram_percent < 90
        else PALETTE["magenta"]
    )
    ram_panel = Panel(
        Group(
            f"[bold {ram_color}]{snapshot.ram_used_gb:.1f} / {snapshot.ram_total_gb:.1f} GB ({snapshot.ram_percent}%)[/bold {ram_color}]",
            ram_bar,
            f"[dim]Free: {snapshot.ram_free_gb:.1f} GB[/dim]",
        ),
        title="[bold]RAM Usage[/bold]",
        border_style=ram_color,
    )

    # Disk Panel
    disk_bar = ProgressBar(total=100, completed=snapshot.disk_percent, width=18)
    disk_color = (
        PALETTE["green"]
        if snapshot.disk_percent < 75
        else PALETTE["yellow"]
        if snapshot.disk_percent < 90
        else PALETTE["magenta"]
    )
    disk_panel = Panel(
        Group(
            f"[bold {disk_color}]{snapshot.disk_used_gb:.1f} / {snapshot.disk_total_gb:.1f} GB ({snapshot.disk_percent}%)[/bold {disk_color}]",
            disk_bar,
            f"[dim]Free: {snapshot.disk_free_gb:.1f} GB[/dim]",
        ),
        title="[bold]Disk Space[/bold]",
        border_style=disk_color,
    )

    metrics_table.add_row(cpu_panel, ram_panel, disk_panel)
    layout["metrics"].update(metrics_table)

    # 3. Top Processes Table
    proc_table = Table(
        title="Top Resource-Consuming Processes",
        border_style=PALETTE["blue"],
        header_style=f"bold {PALETTE['cyan']}",
        expand=True,
    )
    proc_table.add_column("PID", style="dim", width=8)
    proc_table.add_column("Process Name", style=f"bold {PALETTE['green']}")
    proc_table.add_column("Memory (MB)", justify="right", style=f"{PALETTE['magenta']}")
    proc_table.add_column("RAM %", justify="right")
    proc_table.add_column("CPU %", justify="right")
    proc_table.add_column("Status", style="dim", justify="center")

    for p in snapshot.top_processes:
        proc_table.add_row(
            str(p.pid),
            p.name,
            f"{p.memory_mb:.1f} MB",
            f"{p.memory_percent:.1f}%",
            f"{p.cpu_percent:.1f}%",
            p.status,
        )

    layout["processes"].update(proc_table)
    return layout


@app.callback(invoke_without_command=True)
def monitor_main(
    ctx: typer.Context,
    live: bool = typer.Option(
        False, "--live", "-l", help="Run in continuous live dashboard mode (Ctrl+C to stop)"
    ),
    interval: float = typer.Option(
        2.0, "--interval", "-i", help="Refresh interval in seconds for live mode"
    ),
) -> None:
    """System resource and hardware monitor."""
    if not live:
        snapshot = get_system_snapshot(top_n=8)
        console.print(get_theme_header("System & Hardware Resource Monitor"))
        console.print(render_monitor_view(snapshot))
        console.print(
            f"\n[dim]Tip: Run with [bold {PALETTE['cyan']}]cassandra monitor --live[/bold {PALETTE['cyan']}] for real-time auto-refresh.[/dim]"
        )
        return

    console.print(
        f"[{PALETTE['cyan']}]Starting live system monitor (Press Ctrl+C to exit)...[/{PALETTE['cyan']}]"
    )
    try:
        with Live(
            render_monitor_view(get_system_snapshot(top_n=8)),
            console=console,
            refresh_per_second=4,
            screen=True,
        ) as live_view:
            while True:
                time.sleep(interval)
                snapshot = get_system_snapshot(top_n=8)
                live_view.update(render_monitor_view(snapshot))
    except KeyboardInterrupt:
        console.print(f"[{PALETTE['green']}]Monitor closed.[/{PALETTE['green']}]")
