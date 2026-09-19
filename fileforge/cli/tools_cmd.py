from pathlib import Path

import typer
from rich.panel import Panel
from rich.prompt import Confirm
from rich.text import Text

from fileforge.modules.git_intel import check_project_health, get_git_status
from fileforge.modules.tools import (
    analyze_disk_usage,
    clean_junk_directories,
    create_archive,
    execute_batch_rename,
    extract_archive,
    find_duplicate_files,
    plan_batch_rename,
)
from fileforge.ui.theme import console, create_table, error_console

tools_app = typer.Typer(help="Advanced file, storage, and repository tools")


@tools_app.command("duplicates")
def duplicates_cmd(
    path: Path = typer.Argument(Path("."), help="Directory to search for duplicate files"),
    min_size: int = typer.Option(1, "--min-size", "-m", help="Minimum file size in bytes to check"),
):
    """Find duplicate files based on SHA-256 hash comparison."""
    try:
        with console.status("[bold cyan]Scanning directory for duplicate files...[/bold cyan]"):
            groups = find_duplicate_files(path, min_size_bytes=min_size)

        if not groups:
            console.print("[bold green]✓ No duplicate files found in directory![/bold green]")
            return

        total_wasted = sum(g.file_size * (len(g.files) - 1) for g in groups)
        wasted_mb = total_wasted / (1024 * 1024)

        table = create_table(
            title=f"🔍 Duplicate Files Found ({len(groups)} groups, ~{wasted_mb:.2f} MB potential savings)",
            columns=["Hash (SHA-256)", "File Size", "Duplicate File Copies"],
        )
        for g in groups:
            files_list = "\n".join(str(p.name) for p in g.files)
            table.add_row(
                f"[dim]{g.file_hash[:16]}...[/dim]",
                f"{g.file_size / 1024:.1f} KB",
                f"[cyan]{files_list}[/cyan]",
            )

        console.print(table)
    except Exception as e:
        error_console.print(f"[error]Duplicate scan failed:[/error] {e}")
        raise typer.Exit(1)


@tools_app.command("disk")
def disk_cmd(
    path: Path = typer.Argument(Path("."), help="Directory to analyze for disk usage"),
    clean: bool = typer.Option(
        False, "--clean", "-c", help="Clean detected build/cache junk directories"
    ),
):
    """Analyze storage usage of subdirectories and optionally clean junk."""
    try:
        with console.status("[bold cyan]Analyzing directory storage usage...[/bold cyan]"):
            items = analyze_disk_usage(path)

        table = create_table(
            title=f"📊 Storage Usage: {path.resolve()}",
            columns=["Directory", "Size", "Junk/Cache Candidate?"],
        )
        for it in items:
            junk_badge = (
                "[bold yellow]YES (Junk/Cache)[/bold yellow]"
                if it.is_junk_candidate
                else "[dim]No[/dim]"
            )
            dir_style = "bold yellow" if it.is_junk_candidate else "cyan"
            table.add_row(f"[{dir_style}]{it.name}[/{dir_style}]", it.formatted_size, junk_badge)

        console.print(table)

        if clean:
            if Confirm.ask(
                "\n[bold red]Clean identified junk/cache folders (node_modules, .venv, build, etc.)?[/bold red]"
            ):
                cleaned, freed = clean_junk_directories(path, dry_run=False)
                console.print(
                    f"[bold green]✓ Cleaned {cleaned} folders! Freed {freed / (1024 * 1024):.2f} MB.[/bold green]"
                )
    except Exception as e:
        error_console.print(f"[error]Disk analysis failed:[/error] {e}")
        raise typer.Exit(1)


@tools_app.command("rename")
def rename_cmd(
    path: Path = typer.Argument(Path("."), help="Directory containing files to rename"),
    pattern: str = typer.Option("", "--pattern", "-p", help="Regex pattern to match in filenames"),
    replace: str = typer.Option("", "--replace", "-r", help="Replacement text for pattern"),
    prefix: str = typer.Option("", "--prefix", help="Prefix to prepend to filename"),
    suffix: str = typer.Option("", "--suffix", help="Suffix to append to filename stem"),
    numbering: bool = typer.Option(
        False, "--numbering", "-n", help="Append sequential numbering (_001, _002)"
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Execute rename operations (default is dry-run preview)"
    ),
):
    """Batch rename files using pattern matching, prefixes, or numbering."""
    try:
        plans = plan_batch_rename(
            path,
            pattern=pattern,
            replacement=replace,
            prefix=prefix,
            suffix=suffix,
            numbering=numbering,
        )
        if not plans:
            console.print("[dim]No files found to rename.[/dim]")
            return

        table = create_table(
            title=f"🏷️ Batch Rename Plan {'(PREVIEW)' if not apply else '(APPLYING)'}",
            columns=["Original Name", "New Name", "Collision?"],
        )
        for p in plans:
            coll_badge = (
                "[bold red]YES (Will Skip)[/bold red]" if p.collision else "[green]No[/green]"
            )
            table.add_row(p.original_path.name, f"[cyan]{p.new_path.name}[/cyan]", coll_badge)

        console.print(table)

        if not apply:
            console.print(
                "\n[bold yellow]ℹ This is a dry-run preview. Use '--apply' to execute changes.[/bold yellow]"
            )
        else:
            if Confirm.ask("[bold magenta]Proceed with batch rename?[/bold magenta]"):
                renamed = execute_batch_rename(plans, dry_run=False)
                console.print(f"[bold green]✓ Renamed {renamed} files successfully![/bold green]")
    except Exception as e:
        error_console.print(f"[error]Batch rename failed:[/error] {e}")
        raise typer.Exit(1)


@tools_app.command("zip")
def zip_cmd(
    source: Path = typer.Argument(..., help="Source file or directory to compress"),
    output: Path | None = typer.Option(
        None, "--out", "-o", help="Target output archive path (.zip / .tar.gz)"
    ),
    tar: bool = typer.Option(False, "--tar", help="Create .tar.gz archive instead of .zip"),
):
    """Compress a file or directory into a zip or tar archive."""
    try:
        archive_type = "tar.gz" if tar else "zip"
        with console.status(f"[bold cyan]Compressing {source.name}...[/bold cyan]"):
            out_file = create_archive(source, output_file=output, archive_type=archive_type)
        console.print(f"[bold green]✓ Archive created:[/bold green] [cyan]{out_file}[/cyan]")
    except Exception as e:
        error_console.print(f"[error]Compression failed:[/error] {e}")
        raise typer.Exit(1)


@tools_app.command("unzip")
def unzip_cmd(
    archive: Path = typer.Argument(..., help="Archive file to extract (.zip, .tar, .tar.gz)"),
    dest: Path | None = typer.Option(None, "--dest", "-d", help="Destination extract directory"),
):
    """Safely extract an archive file with Zip-Slip protection."""
    try:
        with console.status(f"[bold cyan]Extracting {archive.name}...[/bold cyan]"):
            out_dir = extract_archive(archive, dest_dir=dest)
        console.print(
            f"[bold green]✓ Archive extracted safely to:[/bold green] [cyan]{out_dir}[/cyan]"
        )
    except Exception as e:
        error_console.print(f"[error]Extraction failed:[/error] {e}")
        raise typer.Exit(1)


@tools_app.command("health")
def health_cmd(
    path: Path = typer.Argument(Path("."), help="Project root directory to analyze"),
):
    """Evaluate repository and codebase health score."""
    try:
        health = check_project_health(path)
        git = get_git_status(path)

        score_color = "green" if health.score >= 80 else ("yellow" if health.score >= 50 else "red")

        info_text = Text()
        info_text.append(f"📁 Project: {path.resolve().name}\n", style="bold cyan")
        info_text.append("🌿 Git: ", style="bold magenta")
        if git.is_repo:
            info_text.append(
                f"Branch '{git.branch}' • {'Clean' if git.is_clean else f'Dirty (+{git.modified_count} mod, +{git.untracked_count} untracked)'}\n",
                style="green" if git.is_clean else "yellow",
            )
        else:
            info_text.append("Not a git repository\n", style="dim")
        info_text.append("🏆 Health Score: ", style="bold white")
        info_text.append(f"{health.score}/100\n", style=f"bold {score_color}")

        console.print(Panel(info_text, title="🩺 Project Health Evaluation", border_style="cyan"))

        table = create_table(
            title="Health Checklist", columns=["Status", "Check Item", "Description"]
        )
        for c in health.checks:
            status_str = (
                "[bold green]✓ PASS[/bold green]" if c.passed else "[bold red]✗ MISSING[/bold red]"
            )
            table.add_row(status_str, c.name, c.description)
        console.print(table)

        if health.suggestions:
            sugg_text = Text()
            sugg_text.append("💡 Suggestions for improvement:\n", style="bold yellow")
            for s in health.suggestions:
                sugg_text.append(f" • {s}\n", style="white")
            console.print(Panel(sugg_text, border_style="dim yellow"))
    except Exception as e:
        error_console.print(f"[error]Health check failed:[/error] {e}")
        raise typer.Exit(1)
