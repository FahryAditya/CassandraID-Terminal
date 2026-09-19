from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cassandra_terminal.modules.runner import detect_project_scripts, execute_script
from cassandra_terminal.ui.theme import PALETTE, get_theme_header

app = typer.Typer(
    name="run",
    help="⚡ Universal project script & task runner (npm, python, make, cargo, etc.)",
    no_args_is_help=False,
)
console = Console()


@app.callback(invoke_without_command=True)
def run_main(
    ctx: typer.Context,
    script_name: str = typer.Argument(
        None, help="Name of the script to run (leave blank for interactive list)"
    ),
    list_only: bool = typer.Option(
        False, "--list", "-l", help="Only list available scripts without running"
    ),
) -> None:
    """Universal script runner. Detects scripts from package.json, pyproject.toml, Makefile, etc."""
    scripts = detect_project_scripts()

    if not scripts:
        console.print(get_theme_header("Universal Script Runner"))
        console.print(
            Panel(
                "[yellow]No runnable scripts or task configurations detected in the current directory.[/yellow]\n\n"
                "[dim]Supported sources: package.json, pyproject.toml, Makefile, Cargo.toml, scripts/ folder[/dim]",
                title="[bold red]No Scripts Found[/bold red]",
                border_style=PALETTE["blue"],
            )
        )
        return

    # If user provided a specific script name directly
    if script_name:
        matched = [s for s in scripts if s.name.lower() == script_name.lower()]
        if matched:
            selected = matched[0]
            console.print(
                f"[{PALETTE['cyan']}]⚡ Running [{PALETTE['green']}]{selected.name}[/{PALETTE['green']}] "
                f"via [dim]{selected.command}[/dim]...[/{PALETTE['cyan']}]\n"
            )
            code = execute_script(selected.command)
            if code != 0:
                raise typer.Exit(code=code)
            return
        else:
            console.print(
                f"[{PALETTE['magenta']}]⚠ Script '{script_name}' not found.[/{PALETTE['magenta']}] "
                f"Available scripts: {', '.join(s.name for s in scripts)}"
            )
            raise typer.Exit(code=1)

    # Display list table
    console.print(get_theme_header("Universal Project Task & Script Runner"))

    table = Table(
        title=f"Discovered Project Scripts ({len(scripts)})",
        border_style=PALETTE["blue"],
        header_style=f"bold {PALETTE['cyan']}",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Script Name", style=f"bold {PALETTE['green']}")
    table.add_column("Source", style=f"bold {PALETTE['magenta']}")
    table.add_column("Command / Target", style="dim")

    for idx, s in enumerate(scripts, 1):
        table.add_row(str(idx), s.name, s.source, s.command)

    console.print(table)

    if list_only:
        return

    console.print(
        f"\n[{PALETTE['cyan']}]Enter the script number or name to run ([dim]or press Enter to cancel[/dim]):[/{PALETTE['cyan']}]"
    )
    choice = typer.prompt("Select script", default="", show_default=False).strip()

    if not choice:
        console.print(f"[{PALETTE['yellow']}]Cancelled.[/{PALETTE['yellow']}]")
        return

    selected_script = None
    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(scripts):
            selected_script = scripts[idx - 1]
    else:
        matched = [s for s in scripts if s.name.lower() == choice.lower()]
        if matched:
            selected_script = matched[0]

    if not selected_script:
        console.print(f"[{PALETTE['magenta']}]Invalid selection.[/{PALETTE['magenta']}]")
        raise typer.Exit(code=1)

    console.print(
        f"\n[{PALETTE['cyan']}]⚡ Executing [{PALETTE['green']}]{selected_script.name}[/{PALETTE['green']}] "
        f"([dim]{selected_script.command}[/dim])...[/{PALETTE['cyan']}]\n"
    )
    code = execute_script(selected_script.command)
    if code != 0:
        raise typer.Exit(code=code)
