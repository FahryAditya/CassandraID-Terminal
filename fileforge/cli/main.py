import sys
from pathlib import Path

import typer

# Ensure UTF-8 output encoding across Windows terminals
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fileforge import __app_name__, __version__
from fileforge.cli.files_cmd import files_app
from fileforge.cli.misc_cmd import history_cmd, settings_app
from fileforge.cli.project_cmd import create_cmd, templates_app
from fileforge.cli.tools_cmd import tools_app
from fileforge.cli.workspace_cmd import projects_app, workspace_app
from fileforge.modules.dashboard import render_dashboard, run_interactive_dashboard
from fileforge.ui.theme import console

app = typer.Typer(
    name=__app_name__,
    help="⚡ CassandraID-Terminal - A local-first developer workspace toolkit and intelligence center for the terminal.",
    no_args_is_help=False,
    invoke_without_command=True,
)

# Register Sub-apps
app.add_typer(files_app, name="files")
app.add_typer(tools_app, name="tools")
app.add_typer(templates_app, name="templates")
app.add_typer(workspace_app, name="workspace")
app.add_typer(projects_app, name="projects")
app.add_typer(settings_app, name="settings")

# Register direct commands
app.command(name="create")(create_cmd)
app.command(name="history")(history_cmd)


def version_callback(value: bool):
    if value:
        console.print(
            f"[bold cyan]{__app_name__}[/bold cyan] version [magenta]{__version__}[/magenta]"
        )
        raise typer.Exit()


@app.command(name="dashboard")
def dashboard_command(
    path: Path = typer.Option(
        Path("."), "--path", "-p", help="Target working directory for dashboard context"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", "-i/-n", help="Run interactive action menu"
    ),
):
    """Launch the terminal Command Center dashboard with action selection."""
    if interactive:
        run_interactive_dashboard(path)
    else:
        render_dashboard(path)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show application version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
):
    """FileForge DevKit CLI Entrypoint."""
    if ctx.invoked_subcommand is None:
        # Default behavior when running just `fileforge`
        run_interactive_dashboard(Path("."))


if __name__ == "__main__":
    app()
