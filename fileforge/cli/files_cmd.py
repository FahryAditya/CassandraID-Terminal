from pathlib import Path

import typer
from rich.prompt import Confirm
from rich.tree import Tree

from fileforge.modules.files import (
    execute_organize,
    list_directory,
    plan_organize,
    safe_copy,
    safe_delete,
    safe_move,
    safe_rename,
    search_files,
)
from fileforge.modules.tui import run_tui_file_browser
from fileforge.ui.theme import console, create_table, error_console

files_app = typer.Typer(help="File & directory management commands (FileForge)")


@files_app.command("browse")
def browse_cmd(
    path: Path = typer.Argument(Path("."), help="Target root directory to browse interactively"),
):
    """Launch interactive dual-pane TUI file browser with live preview."""
    try:
        run_tui_file_browser(path)
    except Exception as e:
        error_console.print(f"[error]TUI browser exited with error:[/error] {e}")
        raise typer.Exit(1)


@files_app.command("list")
def list_cmd(
    path: Path = typer.Argument(Path("."), help="Target directory path"),
    sort: str = typer.Option("name", "--sort", "-s", help="Sort by: name, size, date, type"),
    reverse: bool = typer.Option(False, "--reverse", "-r", help="Reverse sorting"),
    all_files: bool = typer.Option(False, "--all", "-a", help="Include hidden files"),
):
    """List contents of a directory with detailed metadata."""
    try:
        items = list_directory(path, sort_by=sort, reverse=reverse, show_hidden=all_files)
        table = create_table(
            title=f"📁 Directory: {path.resolve()}",
            columns=["Type", "Name", "Size", "Modified Date"],
        )
        for item in items:
            type_badge = (
                "[bold magenta]<DIR>[/bold magenta]" if item.is_dir else "[cyan]FILE[/cyan]"
            )
            name_style = "bold cyan" if item.is_dir else "white"
            table.add_row(
                type_badge,
                f"[{name_style}]{item.name}[/{name_style}]",
                item.formatted_size,
                item.formatted_time,
            )

        console.print(table)
        console.print(f"[dim]Total items: {len(items)}[/dim]")
    except Exception as e:
        error_console.print(f"[error]Error listing directory:[/error] {e}")
        raise typer.Exit(1)


@files_app.command("tree")
def tree_cmd(
    path: Path = typer.Argument(Path("."), help="Target root directory"),
    depth: int = typer.Option(3, "--depth", "-d", help="Max tree depth"),
):
    """Display visual tree hierarchy of a directory."""
    root_path = path.resolve()
    if not root_path.exists() or not root_path.is_dir():
        error_console.print(f"[error]Invalid directory path:[/error] {root_path}")
        raise typer.Exit(1)

    tree = Tree(f"[bold cyan]📁 {root_path.name}[/bold cyan] [dim]({root_path})[/dim]")

    def build_branch(dir_path: Path, current_branch: Tree, current_depth: int):
        if current_depth > depth:
            return
        try:
            entries = sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            for entry in entries:
                if entry.name.startswith("."):
                    continue
                if entry.is_dir():
                    branch = current_branch.add(f"[bold magenta]📁 {entry.name}[/bold magenta]")
                    build_branch(entry, branch, current_depth + 1)
                else:
                    current_branch.add(f"[white]📄 {entry.name}[/white]")
        except PermissionError:
            current_branch.add("[red][Access Denied][/red]")

    build_branch(root_path, tree, 1)
    console.print(tree)


@files_app.command("search")
def search_cmd(
    query: str = typer.Argument("", help="Search query / filename pattern"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Root directory to search"),
    extension: str | None = typer.Option(
        None, "--ext", "-e", help="Filter by extension (e.g. py, js, md)"
    ),
    recursive: bool = typer.Option(
        True, "--recursive/--no-recursive", "-R", help="Search subdirectories"
    ),
    case_sensitive: bool = typer.Option(
        False, "--case-sensitive", "-c", help="Case-sensitive matching"
    ),
):
    """Search for files and directories."""
    try:
        results = search_files(
            target_path=path,
            query=query,
            extension=extension,
            recursive=recursive,
            case_sensitive=case_sensitive,
        )
        table = create_table(
            title=f"🔍 Search Results for '{query}' (Found: {len(results)})",
            columns=["Type", "Name", "Size", "Path"],
        )
        for item in results:
            type_badge = (
                "[bold magenta]<DIR>[/bold magenta]" if item.is_dir else "[cyan]FILE[/cyan]"
            )
            table.add_row(type_badge, item.name, item.formatted_size, str(item.path.resolve()))
        console.print(table)
    except Exception as e:
        error_console.print(f"[error]Search failed:[/error] {e}")
        raise typer.Exit(1)


@files_app.command("copy")
def copy_cmd(
    source: Path = typer.Argument(..., help="Source file or directory"),
    dest: Path = typer.Argument(..., help="Destination path"),
    overwrite: bool = typer.Option(
        False, "--overwrite", "-f", help="Force overwrite existing files"
    ),
):
    """Safely copy files or directories."""
    try:

        def confirm_prompt(msg: str) -> bool:
            return Confirm.ask(f"[bold yellow]{msg}[/bold yellow]")

        result_path = safe_copy(source, dest, overwrite=overwrite, confirm_callback=confirm_prompt)
        console.print(
            f"[bold green]✓ Successfully copied[/bold green] [cyan]{source}[/cyan] -> [cyan]{result_path}[/cyan]"
        )
    except Exception as e:
        error_console.print(f"[error]Copy failed:[/error] {e}")
        raise typer.Exit(1)


@files_app.command("move")
def move_cmd(
    source: Path = typer.Argument(..., help="Source file or directory"),
    dest: Path = typer.Argument(..., help="Destination path"),
    overwrite: bool = typer.Option(
        False, "--overwrite", "-f", help="Force overwrite existing files"
    ),
):
    """Safely move files or directories."""
    try:

        def confirm_prompt(msg: str) -> bool:
            return Confirm.ask(f"[bold yellow]{msg}[/bold yellow]")

        result_path = safe_move(source, dest, overwrite=overwrite, confirm_callback=confirm_prompt)
        console.print(
            f"[bold green]✓ Successfully moved[/bold green] [cyan]{source}[/cyan] -> [cyan]{result_path}[/cyan]"
        )
    except Exception as e:
        error_console.print(f"[error]Move failed:[/error] {e}")
        raise typer.Exit(1)


@files_app.command("rename")
def rename_cmd(
    source: Path = typer.Argument(..., help="Target file or directory to rename"),
    new_name: str = typer.Argument(..., help="New filename (not a path)"),
):
    """Safely rename a file or directory."""
    try:
        result_path = safe_rename(source, new_name)
        console.print(
            f"[bold green]✓ Successfully renamed to[/bold green] [cyan]{result_path.name}[/cyan]"
        )
    except Exception as e:
        error_console.print(f"[error]Rename failed:[/error] {e}")
        raise typer.Exit(1)


@files_app.command("delete")
def delete_cmd(
    path: Path = typer.Argument(..., help="Target file or directory to delete"),
    recursive: bool = typer.Option(
        False, "--recursive", "-r", help="Recursively delete non-empty directory"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirm deletion without prompting"),
):
    """Permanently delete a file or directory (safeguarded)."""
    try:

        def confirm_prompt(msg: str) -> bool:
            if yes:
                return True
            return Confirm.ask(f"[bold red]{msg}[/bold red]")

        safe_delete(path, recursive=recursive, confirm_callback=confirm_prompt)
        console.print(f"[bold green]✓ Successfully deleted[/bold green] [cyan]{path}[/cyan]")
    except Exception as e:
        error_console.print(f"[error]Delete failed:[/error] {e}")
        raise typer.Exit(1)


@files_app.command("organize")
def organize_cmd(
    path: Path = typer.Argument(Path("."), help="Directory to organize"),
    dry_run: bool = typer.Option(
        True, "--dry-run/--apply", help="Preview moves without making actual changes"
    ),
):
    """Organize messy directory into categorical subfolders (Images, Docs, Code, etc.)."""
    try:
        plans = plan_organize(path)
        if not plans:
            console.print("[dim]No files to organize in directory.[/dim]")
            return

        table = create_table(
            title=f"📦 Organization Plan {'(DRY-RUN PREVIEW)' if dry_run else '(APPLYING)'}",
            columns=["File", "Category", "Destination", "Collision?"],
        )
        for p in plans:
            collision_str = "[red]YES (Will Skip)[/red]" if p.collision else "[green]No[/green]"
            table.add_row(
                p.source.name, f"[cyan]{p.category}[/cyan]", str(p.destination), collision_str
            )

        console.print(table)

        if dry_run:
            console.print(
                "\n[bold yellow]ℹ This was a dry-run. Pass '--apply' to execute the organization.[/bold yellow]"
            )
        else:
            if Confirm.ask("[bold magenta]Proceed with organizing files?[/bold magenta]"):
                moved = execute_organize(plans, dry_run=False)
                console.print(f"[bold green]✓ Organized {moved} files successfully![/bold green]")
            else:
                console.print("[dim]Operation cancelled.[/dim]")
    except Exception as e:
        error_console.print(f"[error]Organize failed:[/error] {e}")
        raise typer.Exit(1)
