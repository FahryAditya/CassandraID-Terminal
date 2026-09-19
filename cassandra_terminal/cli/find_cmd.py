from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cassandra_terminal.modules.finder import find_files_fuzzy, open_file_in_editor
from cassandra_terminal.ui.theme import PALETTE, get_theme_header

app = typer.Typer(
    name="find",
    help="🔍 Live fuzzy file search & instant editor launcher",
    no_args_is_help=False,
)
console = Console()


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


@app.callback(invoke_without_command=True)
def find_main(
    ctx: typer.Context,
    query: str = typer.Argument(
        "", help="File name, pattern, or substring to search for (empty for interactive prompt)"
    ),
    open_first: bool = typer.Option(
        False, "--open", "-o", help="Immediately open the top matching file in editor"
    ),
    editor: str = typer.Option(
        None, "--editor", "-e", help="Specific editor command (code, cursor, nvim, vim, etc.)"
    ),
    limit: int = typer.Option(15, "--limit", "-n", help="Maximum number of results to display"),
) -> None:
    """Live fuzzy file finder and editor launcher."""
    search_query = query.strip()
    if not search_query:
        console.print(get_theme_header("Fuzzy File Finder & Editor Launcher"))
        search_query = typer.prompt("Enter search term / file pattern", default="").strip()
        if not search_query:
            console.print(
                f"[{PALETTE['yellow']}]No search query provided. Exiting.[/{PALETTE['yellow']}]"
            )
            return

    results = find_files_fuzzy(search_query, limit=limit)

    if not results:
        console.print(
            Panel(
                f"[yellow]No files matched query '[bold]{search_query}[/bold]' in this workspace.[/yellow]",
                title="[bold red]Search Complete[/bold red]",
                border_style=PALETTE["blue"],
            )
        )
        return

    if open_first:
        top_match = results[0]
        console.print(
            f"[{PALETTE['cyan']}]🚀 Opening top match: [{PALETTE['green']}]{top_match.relative_path}[/{PALETTE['green']}]...[/{PALETTE['cyan']}]"
        )
        opened = open_file_in_editor(top_match.path, editor=editor)
        if not opened:
            console.print(
                f"[{PALETTE['magenta']}]⚠ Could not launch editor automatically for {top_match.path}[/{PALETTE['magenta']}]"
            )
        return

    console.print(get_theme_header("Fuzzy File Finder Results"))

    table = Table(
        title=f"Matches for '{search_query}' ({len(results)} results)",
        border_style=PALETTE["blue"],
        header_style=f"bold {PALETTE['cyan']}",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("File Path", style=f"bold {PALETTE['green']}")
    table.add_column("Size", style="dim", justify="right")
    table.add_column("Relevance", style=f"{PALETTE['magenta']}", justify="right")

    for idx, item in enumerate(results, 1):
        rel_badge = f"{int(item.score)}%" if item.score <= 100 else "100%"
        size_str = "-" if item.is_dir else format_size(item.size)
        table.add_row(str(idx), item.relative_path, size_str, rel_badge)

    console.print(table)

    console.print(
        f"\n[{PALETTE['cyan']}]Enter file # to open in editor ([dim]or press Enter to exit[/dim]):[/{PALETTE['cyan']}]"
    )
    choice = typer.prompt("Select file", default="", show_default=False).strip()

    if not choice:
        return

    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(results):
            selected = results[idx - 1]
            console.print(
                f"[{PALETTE['cyan']}]🚀 Opening [{PALETTE['green']}]{selected.relative_path}[/{PALETTE['green']}]...[/{PALETTE['cyan']}]"
            )
            opened = open_file_in_editor(selected.path, editor=editor)
            if not opened:
                console.print(
                    f"[{PALETTE['magenta']}]⚠ Could not launch editor automatically. Path: {selected.path}[/{PALETTE['magenta']}]"
                )
        else:
            console.print(f"[{PALETTE['magenta']}]Selection out of range.[/{PALETTE['magenta']}]")
