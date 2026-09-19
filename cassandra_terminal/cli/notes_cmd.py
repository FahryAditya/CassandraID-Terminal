from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cassandra_terminal.modules.notes import (
    add_note,
    clear_completed_notes,
    delete_note,
    list_notes,
    toggle_note_status,
)
from cassandra_terminal.ui.theme import PALETTE, get_theme_header

app = typer.Typer(
    name="notes",
    help="📝 Project scratchpad & TODO checklist tracker",
    no_args_is_help=False,
)
console = Console()


@app.callback(invoke_without_command=True)
def notes_main(
    ctx: typer.Context,
    filter_status: str = typer.Option(
        "all", "--status", "-s", help="Filter notes: all, pending, done"
    ),
) -> None:
    """List all notes and TODOs for the current project."""
    if ctx.invoked_subcommand is not None:
        return

    status_filter = filter_status.lower()
    if status_filter not in ("all", "pending", "done"):
        status_filter = "all"

    notes = list_notes(filter_status=status_filter)  # type: ignore[arg-type]

    console.print(get_theme_header("Project Scratchpad & Task Checklist"))

    if not notes:
        console.print(
            Panel(
                f"[yellow]No notes or tasks found for this workspace.[/yellow]\n\n"
                f'[dim]Tip: Add one with [bold {PALETTE["cyan"]}]cassandra notes add "Fix database query"[/bold {PALETTE["cyan"]}][/dim]',
                title="[bold green]Workspace Notes Clean[/bold green]",
                border_style=PALETTE["blue"],
            )
        )
        return

    table = Table(
        title=f"Project Notes ({len(notes)} items)",
        border_style=PALETTE["blue"],
        header_style=f"bold {PALETTE['cyan']}",
    )
    table.add_column("ID", style="dim", width=4)
    table.add_column("Status", width=10, justify="center")
    table.add_column("Task / Content", style="bold")
    table.add_column("Created", style="dim")

    for n in notes:
        status_badge = (
            f"[{PALETTE['green']}]✔ DONE[/{PALETTE['green']}]"
            if n.status == "done"
            else f"[{PALETTE['yellow']}]⏳ TODO[/{PALETTE['yellow']}]"
        )
        content_styled = (
            f"[dim strike]{n.content}[/dim strike]" if n.status == "done" else n.content
        )
        # Format ISO timestamp
        created_display = n.created_at[:16].replace("T", " ")
        table.add_row(str(n.id), status_badge, content_styled, created_display)

    console.print(table)


@app.command("add")
def notes_add(
    content: str = typer.Argument(..., help="Note / task description to add"),
) -> None:
    """Add a new task or note to current workspace."""
    new_id = add_note(content)
    console.print(
        f"[{PALETTE['green']}]✔ Task added successfully (ID: [bold]{new_id}[/bold]): {content}[/{PALETTE['green']}]"
    )


@app.command("done")
def notes_done(
    note_id: int = typer.Argument(..., help="ID of note to toggle completion status"),
) -> None:
    """Toggle completion status of a note (Pending <-> Done)."""
    success, new_status = toggle_note_status(note_id)
    if not success:
        console.print(
            f"[{PALETTE['magenta']}]⚠ Note with ID {note_id} not found.[/{PALETTE['magenta']}]"
        )
        raise typer.Exit(code=1)

    status_str = "completed (done) ✔" if new_status == "done" else "marked pending ⏳"
    console.print(f"[{PALETTE['green']}]✔ Task #{note_id} {status_str}[/{PALETTE['green']}]")


@app.command("delete")
def notes_delete(
    note_id: int = typer.Argument(..., help="ID of note to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
) -> None:
    """Delete a note by ID."""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete note #{note_id}?")
        if not confirm:
            console.print(f"[{PALETTE['yellow']}]Cancelled.[/{PALETTE['yellow']}]")
            return

    if delete_note(note_id):
        console.print(f"[{PALETTE['green']}]✔ Note #{note_id} removed.[/{PALETTE['green']}]")
    else:
        console.print(f"[{PALETTE['magenta']}]⚠ Note #{note_id} not found.[/{PALETTE['magenta']}]")
        raise typer.Exit(code=1)


@app.command("clean")
def notes_clean() -> None:
    """Remove all completed tasks from the current project."""
    count = clear_completed_notes()
    console.print(
        f"[{PALETTE['green']}]✔ Cleaned up {count} completed task(s) from workspace.[/{PALETTE['green']}]"
    )
