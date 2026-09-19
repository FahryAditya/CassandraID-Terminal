from pathlib import Path

import typer

from fileforge.modules.workspace import (
    add_workspace,
    get_recent_projects,
    list_workspaces,
    remove_recent_project,
    remove_workspace,
)
from fileforge.ui.theme import console, create_table, error_console

workspace_app = typer.Typer(help="Workspace management commands (Workspace Explorer)")
projects_app = typer.Typer(help="Recent projects tracking commands")


# --- Workspace Subcommands ---


@workspace_app.command("list")
def list_ws_cmd():
    """List all registered workspaces."""
    workspaces = list_workspaces()
    if not workspaces:
        console.print(
            "[dim]No registered workspaces yet. Use 'fileforge workspace add <path>' to add one.[/dim]"
        )
        return

    table = create_table(
        title="🌐 Registered Workspaces",
        columns=["ID", "Name", "Project Type", "Path", "Last Updated"],
    )
    for ws in workspaces:
        table.add_row(
            str(ws.id or "-"),
            f"[bold cyan]{ws.name}[/bold cyan]",
            f"[bold green]{ws.project_type}[/bold green]",
            ws.path,
            ws.updated_at or "-",
        )
    console.print(table)


@workspace_app.command("add")
def add_ws_cmd(
    path: Path = typer.Argument(Path("."), help="Workspace directory path"),
    name: str | None = typer.Option(
        None, "--name", "-n", help="Optional friendly name for workspace"
    ),
):
    """Register a new workspace."""
    try:
        ws = add_workspace(path, name=name)
        console.print(
            f"[bold green]✓ Registered workspace[/bold green] '[bold cyan]{ws.name}[/bold cyan]' ({ws.project_type}) -> [dim]{ws.path}[/dim]"
        )
    except Exception as e:
        error_console.print(f"[error]Failed to add workspace:[/error] {e}")
        raise typer.Exit(1)


@workspace_app.command("remove")
def remove_ws_cmd(
    target: str = typer.Argument(..., help="Workspace name or directory path"),
):
    """Remove a workspace from registry."""
    try:
        removed = remove_workspace(target)
        if removed:
            console.print(f"[bold green]✓ Removed workspace:[/bold green] [cyan]{target}[/cyan]")
        else:
            console.print(f"[bold yellow]Workspace '{target}' not found in registry.[/bold yellow]")
    except Exception as e:
        error_console.print(f"[error]Failed to remove workspace:[/error] {e}")
        raise typer.Exit(1)


# --- Projects Subcommands ---


@projects_app.command("recent")
def recent_projects_cmd(
    limit: int = typer.Option(10, "--limit", "-n", help="Max number of recent projects to display"),
):
    """Show recently created or accessed projects."""
    recent = get_recent_projects(limit=limit)
    if not recent:
        console.print("[dim]No recent projects found.[/dim]")
        return

    table = create_table(
        title="⏱️ Recently Accessed Projects",
        columns=["Project", "Type", "Path", "Last Accessed"],
    )
    for p in recent:
        table.add_row(
            f"[bold cyan]{p.name}[/bold cyan]",
            f"[bold green]{p.project_type}[/bold green]",
            p.path,
            p.last_accessed,
        )
    console.print(table)


@projects_app.command("remove")
def remove_project_cmd(
    target: str = typer.Argument(..., help="Project ID or path to remove from history"),
):
    """Remove a project from recent history without deleting real files."""
    try:
        removed = remove_recent_project(target)
        if removed:
            console.print(f"[bold green]✓ Removed '{target}' from recent history.[/bold green]")
        else:
            console.print(f"[bold yellow]Project '{target}' not found in history.[/bold yellow]")
    except Exception as e:
        error_console.print(f"[error]Failed to remove from history:[/error] {e}")
        raise typer.Exit(1)
