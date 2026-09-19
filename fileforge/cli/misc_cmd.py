import typer
from rich.prompt import Confirm

from fileforge.modules.activity import clear_activity_logs, get_activity_logs
from fileforge.modules.settings import get_all_settings, get_setting, set_setting
from fileforge.ui.theme import console, create_table, error_console

settings_app = typer.Typer(help="User preferences and configuration (Settings)")


# --- History Command ---


def history_cmd(
    limit: int = typer.Option(30, "--limit", "-n", help="Max number of log entries to display"),
    filter_op: str | None = typer.Option(None, "--filter", "-f", help="Filter by operation type"),
    clear: bool = typer.Option(False, "--clear", help="Clear all activity logs"),
):
    """View and search activity log history."""
    if clear:
        if Confirm.ask("[bold red]Are you sure you want to clear all activity logs?[/bold red]"):
            count = clear_activity_logs()
            console.print(f"[bold green]✓ Cleared {count} activity log entries.[/bold green]")
        return

    logs = get_activity_logs(limit=limit, operation_filter=filter_op)
    if not logs:
        console.print("[dim]No activity recorded yet.[/dim]")
        return

    table = create_table(
        title="📜 Activity History",
        columns=["ID", "Timestamp", "Operation", "Target", "Status", "Details"],
    )
    for log_entry in logs:
        status_style = "bold green" if log_entry.result == "SUCCESS" else "bold red"
        table.add_row(
            str(log_entry.id or "-"),
            log_entry.timestamp,
            f"[bold cyan]{log_entry.operation}[/bold cyan]",
            log_entry.target,
            f"[{status_style}]{log_entry.result}[/{status_style}]",
            log_entry.details or "-",
        )
    console.print(table)


# --- Settings Subcommands ---


@settings_app.callback(invoke_without_command=True)
def default_settings_cmd(ctx: typer.Context):
    """Display all settings if no subcommand is passed."""
    if ctx.invoked_subcommand is None:
        settings = get_all_settings()
        table = create_table(
            title="⚙️ FileForge Settings",
            columns=["Setting Key", "Current Value", "Description / Safeguard"],
        )
        descriptions = {
            "theme": "Terminal UI color theme",
            "require_confirmation": "Always prompt before delete/overwrite (Protected)",
            "default_workspace": "Default root workspace directory",
            "max_tree_depth": "Default tree depth for directory visualization",
            "recent_projects_limit": "Max recent projects to track",
        }
        for k, v in settings.items():
            desc = descriptions.get(k, "User defined preference")
            key_style = "bold magenta"
            val_style = "bold green" if v == "true" else "cyan"
            table.add_row(
                f"[{key_style}]{k}[/{key_style}]", f"[{val_style}]{v}[/{val_style}]", desc
            )
        console.print(table)


@settings_app.command("get")
def get_setting_cmd(key: str = typer.Argument(..., help="Setting key name")):
    """Get the value of a specific setting."""
    val = get_setting(key)
    console.print(f"[bold magenta]{key}[/bold magenta] = [bold cyan]{val}[/bold cyan]")


@settings_app.command("set")
def set_setting_cmd(
    key: str = typer.Argument(..., help="Setting key name"),
    value: str = typer.Argument(..., help="New setting value"),
):
    """Update a setting value (safeguarded against insecure configurations)."""
    try:
        set_setting(key, value)
        console.print(
            f"[bold green]✓ Updated setting[/bold green] [magenta]{key}[/magenta] = [cyan]{value}[/cyan]"
        )
    except Exception as e:
        error_console.print(f"[error]Failed to update setting:[/error] {e}")
        raise typer.Exit(1)
