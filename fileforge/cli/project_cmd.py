from pathlib import Path

import typer
from rich.panel import Panel
from rich.text import Text

from fileforge.modules.generator import (
    generate_project,
    get_available_templates,
    preview_template_structure,
)
from fileforge.ui.theme import console, create_table, error_console

templates_app = typer.Typer(help="Template inspection commands")


@templates_app.command("list")
def list_templates_cmd():
    """List all available project scaffolding templates."""
    templates = get_available_templates()
    table = create_table(
        title="⚒️ Available DevForge Project Templates",
        columns=["Key", "Template Name", "Files", "Description"],
    )
    for tpl in templates:
        table.add_row(
            f"[bold cyan]{tpl.key}[/bold cyan]",
            f"[bold magenta]{tpl.name}[/bold magenta]",
            str(len(tpl.files)),
            tpl.description,
        )
    console.print(table)
    console.print(
        "\n[dim]To generate a project, use:[/dim] [green]fileforge create <template_key> <project_name>[/green]"
    )


def create_cmd(
    template: str = typer.Argument(
        ..., help="Template key (e.g. python-cli, nextjs-ts, static-web)"
    ),
    name: str = typer.Argument(..., help="Name of the new project directory"),
    target: Path = typer.Option(
        Path("."), "--target", "-t", help="Parent directory where project will be generated"
    ),
    author: str = typer.Option(
        "Developer", "--author", "-a", help="Author name for project metadata"
    ),
    license_type: str = typer.Option(
        "MIT", "--license", "-l", help="License type (MIT, Apache-2.0, GPL-3.0, etc.)"
    ),
    description: str | None = typer.Option(
        None, "--desc", "-d", help="Short description of the project"
    ),
    git: bool = typer.Option(False, "--git", "-g", help="Initialize a git repository"),
    venv: bool = typer.Option(False, "--venv", "-v", help="Create a Python virtual environment"),
    code: bool = typer.Option(False, "--code", "-c", help="Open project in VS Code after creation"),
    preview: bool = typer.Option(
        False, "--preview", "-p", help="Preview file structure without generating"
    ),
):
    """Scaffold a new project from a DevForge template."""
    try:
        if preview:
            files = preview_template_structure(
                template, name, {"author_name": author, "license": license_type}
            )
            console.print(
                f"\n[bold magenta]Scaffold Preview for '{name}' ({template}):[/bold magenta]"
            )
            for f in files:
                console.print(f"  📄 {f}")
            return

        with console.status(
            f"[bold cyan]Scaffolding {template} project '{name}'...[/bold cyan]", spinner="dots"
        ):
            project_path = generate_project(
                template_key=template,
                project_name=name,
                target_dir=target,
                author_name=author,
                license_type=license_type,
                description=description,
                git_init=git,
                create_venv=venv,
                open_editor=code,
            )

        success_text = Text()
        success_text.append(f"✨ Project '{name}' successfully created!\n", style="bold green")
        success_text.append(f"📁 Location: {project_path}\n", style="cyan")
        success_text.append(f"🛠️ Template: {template}\n\n", style="magenta")
        success_text.append("Next steps:\n", style="bold white")
        success_text.append(f"  cd {name}\n", style="bold yellow")

        if template.startswith("python"):
            success_text.append("  pip install -e .\n", style="yellow")
        elif template == "nextjs-ts":
            success_text.append("  npm install\n  npm run dev\n", style="yellow")

        console.print(Panel(success_text, border_style="green", padding=(1, 2)))
    except Exception as e:
        error_console.print(f"[error]Project generation failed:[/error] {e}")
        raise typer.Exit(1)
