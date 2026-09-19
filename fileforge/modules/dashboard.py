from pathlib import Path

from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from fileforge.modules.activity import clear_activity_logs, get_activity_logs
from fileforge.modules.files import (
    execute_organize,
    list_directory,
    plan_organize,
    search_files,
)
from fileforge.modules.generator import (
    generate_project,
    get_available_templates,
)
from fileforge.modules.git_intel import check_project_health, get_git_status
from fileforge.modules.settings import get_all_settings, set_setting
from fileforge.modules.tools import (
    analyze_disk_usage,
    clean_junk_directories,
    find_duplicate_files,
)
from fileforge.modules.tui import run_tui_file_browser
from fileforge.modules.workspace import (
    add_workspace,
    detect_project_type,
    get_recent_projects,
    list_workspaces,
)
from fileforge.ui.theme import console, create_table


def render_dashboard(current_dir: Path) -> None:
    """Render the Deep Space interactive terminal dashboard."""
    curr_path = current_dir.resolve()
    curr_type = detect_project_type(curr_path)
    git = get_git_status(curr_path)
    health = check_project_health(curr_path)

    # 1. Header Banner
    header_text = Text()
    header_text.append("⚡ CassandraID-Terminal", style="bold cyan")
    header_text.append("  •  Command Center\n", style="bold magenta")
    header_text.append("Local-First Developer Workspace Toolkit\n\n", style="dim")
    header_text.append("📁 Directory: ", style="bold white")
    header_text.append(f"{curr_path} ", style="underline cyan")
    header_text.append(f"[{curr_type}]\n", style="bold green")

    # Git & Health info line
    header_text.append("🌿 Git: ", style="bold magenta")
    if git.is_repo:
        git_badge = f"Branch '{git.branch}' • {'Clean' if git.is_clean else f'Dirty (+{git.modified_count} mod, +{git.untracked_count} untracked)'}"
        header_text.append(f"{git_badge}    ", style="green" if git.is_clean else "yellow")
    else:
        header_text.append("Not a git repo    ", style="dim")

    score_color = (
        "bold green"
        if health.score >= 80
        else ("bold yellow" if health.score >= 50 else "bold red")
    )
    header_text.append(
        f"🩺 Health: [{score_color}]{health.score}/100[/{score_color}]", style="white"
    )

    header_panel = Panel(header_text, border_style="cyan", padding=(1, 2))

    # 2. Left Panel: Recent Projects & Workspaces
    recent_projects = get_recent_projects(limit=5)
    recent_table = Table(
        title="Recent Projects",
        title_style="bold magenta",
        border_style="dim cyan",
        show_header=True,
    )
    recent_table.add_column("Project", style="cyan")
    recent_table.add_column("Type", style="green")
    recent_table.add_column("Path", style="dim")

    if recent_projects:
        for p in recent_projects:
            recent_table.add_row(p.name, p.project_type, p.path)
    else:
        recent_table.add_row("No recent projects", "-", "-")

    workspaces = list_workspaces()
    ws_table = Table(
        title="Registered Workspaces",
        title_style="bold magenta",
        border_style="dim cyan",
        show_header=True,
    )
    ws_table.add_column("Name", style="cyan")
    ws_table.add_column("Type", style="green")
    ws_table.add_column("Path", style="dim")

    if workspaces:
        for w in workspaces:
            ws_table.add_row(w.name, w.project_type, w.path)
    else:
        ws_table.add_row("No registered workspaces", "-", "-")

    left_group = Group(recent_table, ws_table)
    left_panel = Panel(left_group, title="Workspaces & Projects", border_style="magenta")

    # 3. Right Panel: Activity Log & Quick Commands
    activity_logs = get_activity_logs(limit=6)
    act_table = Table(
        title="Recent Activity",
        title_style="bold magenta",
        border_style="dim cyan",
        show_header=True,
    )
    act_table.add_column("Time", style="dim")
    act_table.add_column("Op", style="bold cyan")
    act_table.add_column("Target", style="white")
    act_table.add_column("Status", style="green")

    if activity_logs:
        for log_entry in activity_logs:
            time_short = (
                log_entry.timestamp.split(" ")[-1]
                if " " in log_entry.timestamp
                else log_entry.timestamp
            )
            status_style = "bold green" if log_entry.result == "SUCCESS" else "bold red"
            act_table.add_row(
                time_short,
                log_entry.operation,
                log_entry.target[-25:] if len(log_entry.target) > 25 else log_entry.target,
                f"[{status_style}]{log_entry.result}[/{status_style}]",
            )
    else:
        act_table.add_row("-", "NONE", "No activity recorded yet", "-")

    cmd_help = Text()
    cmd_help.append("⚡ Quick Commands:\n", style="bold cyan")
    cmd_help.append(" • fileforge files browse .        ", style="green")
    cmd_help.append("Interactive TUI Browser\n", style="dim")
    cmd_help.append(" • fileforge tools duplicates .    ", style="green")
    cmd_help.append("Scan duplicate files\n", style="dim")
    cmd_help.append(" • fileforge tools disk . --clean  ", style="green")
    cmd_help.append("Clean build/cache junk\n", style="dim")
    cmd_help.append(" • fileforge tools health .        ", style="green")
    cmd_help.append("Check project health\n", style="dim")

    right_group = Group(act_table, Panel(cmd_help, border_style="dim cyan"))
    right_panel = Panel(right_group, title="Activity & Quick Actions", border_style="cyan")

    # Display columns
    console.print(header_panel)
    console.print(Columns([left_panel, right_panel], equal=True))


def handle_explore_files(current_dir: Path) -> None:
    """Interactive sub-menu for File Explorer."""
    console.print("\n[bold cyan]📁 File Explorer Menu[/bold cyan]")
    console.print("  [bold green]1.[/bold green] List files in current directory")
    console.print("  [bold green]2.[/bold green] View directory tree")
    console.print("  [bold green]3.[/bold green] Search files by name/extension")
    console.print("  [bold green]4.[/bold green] Launch Interactive TUI Browser (Arrow Navigation)")
    console.print("  [bold dim]0.[/bold dim] Back to main menu")

    choice = Prompt.ask(
        "[bold magenta]Select action[/bold magenta]", choices=["1", "2", "3", "4", "0"], default="1"
    )
    if choice == "1":
        items = list_directory(current_dir)
        table = create_table(
            title=f"Files in {current_dir.resolve()}", columns=["Type", "Name", "Size", "Modified"]
        )
        for it in items:
            type_badge = "[bold magenta]<DIR>[/bold magenta]" if it.is_dir else "[cyan]FILE[/cyan]"
            table.add_row(type_badge, it.name, it.formatted_size, it.formatted_time)
        console.print(table)
    elif choice == "2":
        root_path = current_dir.resolve()
        tree = Tree(f"[bold cyan]📁 {root_path.name}[/bold cyan] [dim]({root_path})[/dim]")
        for entry in sorted(root_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            if entry.name.startswith("."):
                continue
            if entry.is_dir():
                sub_t = tree.add(f"[bold magenta]📁 {entry.name}[/bold magenta]")
                try:
                    for sub_entry in sorted(
                        entry.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())
                    )[:10]:
                        if not sub_entry.name.startswith("."):
                            sub_t.add(
                                f"[cyan]{sub_entry.name}[/cyan]"
                                if sub_entry.is_dir()
                                else f"📄 {sub_entry.name}"
                            )
                except Exception:
                    pass
            else:
                tree.add(f"[white]📄 {entry.name}[/white]")
        console.print(tree)
    elif choice == "3":
        q = Prompt.ask("[bold cyan]Enter search query[/bold cyan]", default="")
        ext = Prompt.ask(
            "[bold cyan]Filter by extension (optional, e.g. py, js)[/bold cyan]", default=""
        )
        results = search_files(current_dir, query=q, extension=ext or None)
        table = create_table(
            title=f"Search Results for '{q}'", columns=["Type", "Name", "Size", "Path"]
        )
        for it in results:
            type_badge = "[bold magenta]<DIR>[/bold magenta]" if it.is_dir else "[cyan]FILE[/cyan]"
            table.add_row(type_badge, it.name, it.formatted_size, str(it.path))
        console.print(table)
    elif choice == "4":
        run_tui_file_browser(current_dir)


def handle_create_project(current_dir: Path) -> None:
    """Interactive sub-menu for DevForge Project Generator."""
    templates = get_available_templates()
    console.print("\n[bold magenta]⚒️  DevForge Project Generator[/bold magenta]")
    for idx, tpl in enumerate(templates, 1):
        console.print(
            f"  [bold green]{idx}.[/bold green] [bold cyan]{tpl.key}[/bold cyan] — {tpl.name} [dim]({tpl.description})[/dim]"
        )
    console.print("  [bold dim]0. Cancel[/bold dim]")

    choices = [str(i) for i in range(len(templates) + 1)]
    choice = Prompt.ask(
        "[bold magenta]Select template[/bold magenta]", choices=choices, default="1"
    )
    if choice == "0":
        return

    selected_tpl = templates[int(choice) - 1]
    name = Prompt.ask("[bold cyan]Enter project name[/bold cyan]")
    if not name.strip():
        console.print("[red]Project name cannot be empty.[/red]")
        return

    author = Prompt.ask("[bold cyan]Author name[/bold cyan]", default="Developer")
    desc = Prompt.ask(
        "[bold cyan]Project description[/bold cyan]", default=f"A new {selected_tpl.name} project"
    )
    git_init = Confirm.ask("[bold cyan]Initialize Git repository?[/bold cyan]", default=False)
    create_venv = False
    if selected_tpl.key.startswith("python"):
        create_venv = Confirm.ask(
            "[bold cyan]Create Python virtual environment (.venv)?[/bold cyan]", default=False
        )

    with console.status(
        f"[bold cyan]Generating {selected_tpl.name} project '{name}'...[/bold cyan]"
    ):
        try:
            proj_path = generate_project(
                template_key=selected_tpl.key,
                project_name=name,
                target_dir=current_dir,
                author_name=author,
                description=desc,
                git_init=git_init,
                create_venv=create_venv,
            )
            console.print(
                f"\n[bold green]✓ Project '{name}' created successfully at:[/bold green] [cyan]{proj_path}[/cyan]"
            )
        except Exception as e:
            console.print(f"[bold red]Failed to create project:[/bold red] {e}")


def handle_tools_menu(current_dir: Path) -> None:
    """Interactive sub-menu for Advanced Tools."""
    console.print("\n[bold magenta]🛠️ Advanced File & Repo Tools[/bold magenta]")
    console.print("  [bold green]1.[/bold green] 🔍 Scan Duplicate Files (SHA-256)")
    console.print("  [bold green]2.[/bold green] 📊 Analyze Disk Usage & Clean Junk Folders")
    console.print("  [bold green]3.[/bold green] 🩺 Project Health Evaluation")
    console.print("  [bold dim]0.[/bold dim] Back to main menu")

    choice = Prompt.ask(
        "[bold cyan]Select tool[/bold cyan]", choices=["1", "2", "3", "0"], default="1"
    )
    if choice == "1":
        with console.status("[bold cyan]Scanning for duplicate files...[/bold cyan]"):
            groups = find_duplicate_files(current_dir)
        if not groups:
            console.print("[bold green]✓ No duplicate files found![/bold green]")
        else:
            table = create_table(
                title=f"Duplicate Files ({len(groups)} groups)", columns=["Hash", "Size", "Files"]
            )
            for g in groups:
                table.add_row(
                    g.file_hash[:16] + "...",
                    f"{g.file_size / 1024:.1f} KB",
                    "\n".join(f.name for f in g.files),
                )
            console.print(table)
    elif choice == "2":
        items = analyze_disk_usage(current_dir)
        table = create_table(
            title=f"Disk Usage: {current_dir.resolve().name}", columns=["Folder", "Size", "Junk?"]
        )
        for it in items:
            junk_badge = (
                "[bold yellow]JUNK/CACHE[/bold yellow]" if it.is_junk_candidate else "[dim]No[/dim]"
            )
            table.add_row(it.name, it.formatted_size, junk_badge)
        console.print(table)
        if Confirm.ask("\n[bold red]Clean build/cache junk folders now?[/bold red]", default=False):
            cnt, freed = clean_junk_directories(current_dir, dry_run=False)
            console.print(
                f"[bold green]✓ Cleaned {cnt} folders! Freed {freed / (1024 * 1024):.2f} MB.[/bold green]"
            )
    elif choice == "3":
        health = check_project_health(current_dir)
        console.print(
            f"\n[bold cyan]Project Health Score:[/bold cyan] [bold green]{health.score}/100[/bold green]"
        )
        table = create_table(
            title="Health Checklist", columns=["Status", "Check Item", "Description"]
        )
        for c in health.checks:
            table.add_row(
                "[bold green]PASS[/bold green]" if c.passed else "[bold red]MISSING[/bold red]",
                c.name,
                c.description,
            )
        console.print(table)


def handle_organize_files(current_dir: Path) -> None:
    """Interactive organizer."""
    plans = plan_organize(current_dir)
    if not plans:
        console.print("[dim]No files to organize in this directory.[/dim]")
        return

    table = create_table(
        title="📦 Organization Plan (Preview)", columns=["File", "Category", "Destination"]
    )
    for p in plans:
        table.add_row(p.source.name, f"[cyan]{p.category}[/cyan]", str(p.destination.name))
    console.print(table)

    if Confirm.ask(
        "[bold magenta]Proceed with organizing these files?[/bold magenta]", default=False
    ):
        moved = execute_organize(plans, dry_run=False)
        console.print(f"[bold green]✓ Organized {moved} files successfully![/bold green]")


def handle_workspace_menu(current_dir: Path) -> None:
    """Interactive workspace menu."""
    workspaces = list_workspaces()
    table = create_table(title="🌐 Registered Workspaces", columns=["Name", "Type", "Path"])
    for w in workspaces:
        table.add_row(
            f"[bold cyan]{w.name}[/bold cyan]", f"[bold green]{w.project_type}[/bold green]", w.path
        )
    console.print(table)

    if Confirm.ask(
        f"[bold cyan]Register current folder '{current_dir.resolve().name}' as workspace?[/bold cyan]",
        default=True,
    ):
        ws_name = Prompt.ask(
            "[bold cyan]Workspace name[/bold cyan]", default=current_dir.resolve().name
        )
        add_workspace(current_dir, name=ws_name)
        console.print(f"[bold green]✓ Registered workspace '{ws_name}'[/bold green]")


def handle_activity_history() -> None:
    """Interactive activity history viewer."""
    logs = get_activity_logs(limit=20)
    table = create_table(
        title="📜 Activity Logs", columns=["Time", "Operation", "Target", "Status"]
    )
    for log_entry in logs:
        status_style = "bold green" if log_entry.result == "SUCCESS" else "bold red"
        table.add_row(
            log_entry.timestamp,
            f"[bold cyan]{log_entry.operation}[/bold cyan]",
            log_entry.target,
            f"[{status_style}]{log_entry.result}[/{status_style}]",
        )
    console.print(table)

    if Confirm.ask("[bold red]Do you want to clear activity logs?[/bold red]", default=False):
        cnt = clear_activity_logs()
        console.print(f"[bold green]✓ Cleared {cnt} log entries.[/bold green]")


def handle_settings_menu() -> None:
    """Interactive settings viewer and editor."""
    settings = get_all_settings()
    table = create_table(title="⚙️ Settings", columns=["Key", "Value"])
    for k, v in settings.items():
        table.add_row(f"[bold magenta]{k}[/bold magenta]", f"[bold green]{v}[/bold green]")
    console.print(table)

    if Confirm.ask("[bold cyan]Do you want to modify a setting?[/bold cyan]", default=False):
        key = Prompt.ask("[bold cyan]Setting key[/bold cyan]")
        val = Prompt.ask("[bold cyan]New value[/bold cyan]")
        try:
            set_setting(key, val)
            console.print(f"[bold green]✓ Updated {key} = {val}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Failed to update setting:[/bold red] {e}")


def run_interactive_dashboard(current_dir: Path) -> None:
    """Run interactive Command Center loop with action selection."""
    while True:
        console.print("\n")
        render_dashboard(current_dir)

        menu_text = Text()
        menu_text.append("  [1] ", style="bold green")
        menu_text.append("📁 Explore Files (List / Tree / Search / TUI)\n", style="white")
        menu_text.append("  [2] ", style="bold green")
        menu_text.append("⚒️  Create Project (DevForge Templates)\n", style="white")
        menu_text.append("  [3] ", style="bold green")
        menu_text.append("🛠️  Advanced Tools (Duplicates / Disk Cleaner / Health)\n", style="white")
        menu_text.append("  [4] ", style="bold green")
        menu_text.append("📦 Organize Directory (Tidy messy files)\n", style="white")
        menu_text.append("  [5] ", style="bold green")
        menu_text.append("🌐 Workspace Explorer (Register & View)\n", style="white")
        menu_text.append("  [6] ", style="bold green")
        menu_text.append("⏱️  Recent Projects\n", style="white")
        menu_text.append("  [7] ", style="bold green")
        menu_text.append("📜 Activity History\n", style="white")
        menu_text.append("  [8] ", style="bold green")
        menu_text.append("⚙️  Settings & Preferences\n", style="white")
        menu_text.append("  [9] ", style="bold green")
        menu_text.append("🔄 Refresh Dashboard\n", style="white")
        menu_text.append("  [0] ", style="bold dim")
        menu_text.append("🚪 Exit\n", style="bold red")

        panel = Panel(
            menu_text,
            title="⚡ Action Menu (Choose an action)",
            border_style="bold magenta",
            padding=(0, 1),
        )
        console.print(panel)

        choice = Prompt.ask(
            "[bold cyan]Select an option[/bold cyan]",
            choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            default="1",
        )

        if choice == "1":
            handle_explore_files(current_dir)
        elif choice == "2":
            handle_create_project(current_dir)
        elif choice == "3":
            handle_tools_menu(current_dir)
        elif choice == "4":
            handle_organize_files(current_dir)
        elif choice == "5":
            handle_workspace_menu(current_dir)
        elif choice == "6":
            recents = get_recent_projects()
            table = create_table(
                title="⏱️ Recent Projects", columns=["Name", "Type", "Path", "Last Accessed"]
            )
            for r in recents:
                table.add_row(
                    f"[bold cyan]{r.name}[/bold cyan]",
                    f"[bold green]{r.project_type}[/bold green]",
                    r.path,
                    r.last_accessed,
                )
            console.print(table)
        elif choice == "7":
            handle_activity_history()
        elif choice == "8":
            handle_settings_menu()
        elif choice == "9":
            continue
        elif choice == "0":
            console.print(
                "\n[bold magenta]Thank you for using CassandraID-Terminal! Goodbye 👋[/bold magenta]\n"
            )
            break

        Prompt.ask("\n[dim]Press Enter to return to main dashboard...[/dim]", default="")
