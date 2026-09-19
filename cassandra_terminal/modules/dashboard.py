from __future__ import annotations

from pathlib import Path

from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from cassandra_terminal.modules.activity import clear_activity_logs, get_activity_logs
from cassandra_terminal.modules.files import (
    execute_organize,
    list_directory,
    plan_organize,
    search_files,
)
from cassandra_terminal.modules.finder import find_files_fuzzy, open_file_in_editor
from cassandra_terminal.modules.generator import (
    generate_project,
    get_available_templates,
)
from cassandra_terminal.modules.git_intel import check_project_health, get_git_status
from cassandra_terminal.modules.notes import (
    add_note,
    delete_note,
    list_notes,
    toggle_note_status,
)
from cassandra_terminal.modules.ports import get_active_listening_ports, kill_port_process
from cassandra_terminal.modules.runner import detect_project_scripts, execute_script
from cassandra_terminal.modules.settings import get_all_settings, set_setting
from cassandra_terminal.modules.tools import (
    analyze_disk_usage,
    clean_junk_directories,
    find_duplicate_files,
)
from cassandra_terminal.modules.tui import run_tui_file_browser
from cassandra_terminal.modules.workspace import (
    add_workspace,
    detect_project_type,
    get_recent_projects,
    list_workspaces,
)
from cassandra_terminal.ui.theme import PALETTE, console, create_table


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
    header_text.append(
        "Local-First Developer Workspace Toolkit & Intelligence Center\n\n", style="dim"
    )
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

    # 2. Left Panel: Recent Projects & Registered Workspaces
    recent_projects = get_recent_projects(limit=4)
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

    # Project Notes widget
    notes = list_notes(str(curr_path), filter_status="pending")[:4]
    notes_table = Table(
        title=f"Workspace Tasks ({len(notes)} pending)",
        title_style="bold magenta",
        border_style="dim cyan",
        show_header=True,
    )
    notes_table.add_column("ID", style="dim", width=4)
    notes_table.add_column("Task", style="bold yellow")

    if notes:
        for n in notes:
            notes_table.add_row(str(n.id), n.content[:35])
    else:
        notes_table.add_row("-", "[dim]No pending tasks. Add one with 'cassandra notes'[/dim]")

    left_group = Group(recent_table, notes_table)
    left_panel = Panel(left_group, title="Projects & Tasks", border_style="magenta")

    # 3. Right Panel: Activity Log & Quick Commands
    activity_logs = get_activity_logs(limit=5)
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
    cmd_help.append("⚡ Power Commands:\n", style="bold cyan")
    cmd_help.append(" • cassandra ports          ", style="bold green")
    cmd_help.append("Inspect & kill listening ports\n", style="dim")
    cmd_help.append(" • cassandra run            ", style="bold green")
    cmd_help.append("Run project scripts (npm/make/py)\n", style="dim")
    cmd_help.append(" • cassandra find <query>   ", style="bold green")
    cmd_help.append("Fuzzy file finder + open\n", style="dim")
    cmd_help.append(" • cassandra notes          ", style="bold green")
    cmd_help.append("Workspace task scratchpad\n", style="dim")
    cmd_help.append(" • cassandra monitor        ", style="bold green")
    cmd_help.append("Live CPU / RAM / Disk monitor\n", style="dim")

    right_group = Group(act_table, Panel(cmd_help, border_style="dim cyan"))
    right_panel = Panel(right_group, title="Activity & Power Actions", border_style="cyan")

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
        tree = Tree(f"[bold cyan]📁 {current_dir.resolve().name}[/bold cyan]")
        for it in list_directory(current_dir):
            if it.is_dir:
                tree.add(f"[bold magenta]📁 {it.name}/[/bold magenta]")
            else:
                tree.add(f"[green]📄 {it.name}[/green] [dim]({it.formatted_size})[/dim]")
        console.print(tree)
    elif choice == "3":
        pattern = Prompt.ask(
            "[bold cyan]Enter file name or pattern (*.py, .json, test*)[/bold cyan]"
        )
        matches = search_files(current_dir, pattern)
        table = create_table(
            title=f"Search matches for '{pattern}'",
            columns=["Type", "Name", "Relative Path", "Size"],
        )
        for it in matches:
            type_badge = "[bold magenta]<DIR>[/bold magenta]" if it.is_dir else "[cyan]FILE[/cyan]"
            try:
                rel = str(it.path.relative_to(current_dir.resolve()))
            except Exception:
                rel = str(it.path)
            table.add_row(type_badge, it.name, rel, it.formatted_size)
        console.print(table)
    elif choice == "4":
        run_tui_file_browser(current_dir)


def handle_create_project(current_dir: Path) -> None:
    """Interactive sub-menu for Project Templates generator."""
    templates = get_available_templates()
    console.print("\n[bold cyan]⚒️ Available Project Templates:[/bold cyan]")
    for idx, t in enumerate(templates, 1):
        console.print(
            f"  [bold green]{idx}.[/bold green] [bold white]{t.name}[/bold white] "
            f"([dim]{t.key}[/dim]) - {t.description}"
        )

    choice = Prompt.ask(
        "\n[bold magenta]Select template number (or 0 to cancel)[/bold magenta]", default="1"
    )
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(templates):
        return

    selected_tpl = templates[int(choice) - 1]
    name = Prompt.ask("[bold cyan]Project name[/bold cyan]", default=f"my-{selected_tpl.key}-app")

    init_git = Confirm.ask("[bold cyan]Initialize Git repository?[/bold cyan]", default=True)
    author = Prompt.ask("[bold cyan]Author name[/bold cyan]", default="Developer")
    desc = Prompt.ask(
        "[bold cyan]Project description[/bold cyan]", default="Created with CassandraID-Terminal"
    )

    console.print(f"\n[cyan]Generating project '{name}'...[/cyan]")
    try:
        dest = generate_project(
            template_key=selected_tpl.key,
            project_name=name,
            target_dir=current_dir,
            author_name=author,
            description=desc,
            git_init=init_git,
        )
        console.print(f"[bold green]✓ Project created successfully at {dest}![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Failed to create project:[/bold red] {e}")


def handle_tools_menu(current_dir: Path) -> None:
    """Interactive sub-menu for advanced dev tools."""
    console.print("\n[bold cyan]🛠️ Advanced Dev Tools[/bold cyan]")
    console.print("  [bold green]1.[/bold green] Duplicate File Finder (SHA-256 Hash)")
    console.print("  [bold green]2.[/bold green] Disk Usage Analyzer & Junk Cleaner")
    console.print("  [bold green]3.[/bold green] Project Health & Repo Integrity Score")
    console.print("  [bold dim]0.[/bold dim] Back to main menu")

    choice = Prompt.ask(
        "[bold magenta]Select tool[/bold magenta]", choices=["1", "2", "3", "0"], default="1"
    )
    if choice == "1":
        with console.status("[bold cyan]Scanning for duplicate files...[/bold cyan]"):
            groups = find_duplicate_files(current_dir)
        if not groups:
            console.print(
                "[bold green]✓ No duplicate files found in current workspace![/bold green]"
            )
        else:
            table = create_table(
                title=f"Found {len(groups)} Duplicate Groups",
                columns=["Hash (SHA256)", "Size", "Duplicate Paths"],
            )
            for g in groups:
                paths_str = "\n".join(str(p.relative_to(current_dir)) for p in g.paths)
                table.add_row(g.file_hash[:12] + "...", g.formatted_size, paths_str)
            console.print(table)
    elif choice == "2":
        with console.status("[bold cyan]Analyzing disk usage...[/bold cyan]"):
            usage = analyze_disk_usage(current_dir)
        table = create_table(
            title=f"Disk Usage for {current_dir.resolve().name} (Total: {usage.formatted_total_size})",
            columns=["Category", "Size", "Folder Count"],
        )
        for cat in usage.categories:
            table.add_row(cat.name, cat.formatted_size, str(cat.item_count))
        console.print(table)

        if usage.junk_size > 0:
            if Confirm.ask(
                f"\n[bold yellow]Found {usage.formatted_junk_size} in junk/cache folders. Clean them up?[/bold yellow]",
                default=False,
            ):
                cleaned_bytes, cleaned_dirs = clean_junk_directories(current_dir)
                console.print(
                    f"[bold green]✓ Cleaned {cleaned_dirs} directories and freed {cleaned_bytes / (1024 * 1024):.2f} MB![/bold green]"
                )
    elif choice == "3":
        health = check_project_health(current_dir)
        console.print(
            f"\n[bold cyan]Project Health Score:[/bold cyan] [bold green]{health.score}/100[/bold green]"
        )
        for check in health.checks:
            badge = "[bold green]PASS[/bold green]" if check.passed else "[bold red]FAIL[/bold red]"
            console.print(f"  • {check.name}: {badge} [dim]({check.description})[/dim]")
        if health.suggestions:
            console.print("\n[bold yellow]Suggestions:[/bold yellow]")
            for sug in health.suggestions:
                console.print(f"  ⚡ {sug}")


def handle_organize_files(current_dir: Path) -> None:
    """Interactive organizer."""
    plans = plan_organize(current_dir)
    if not plans:
        console.print(
            "[bold green]✓ Current directory is already clean and organized![/bold green]"
        )
        return

    table = create_table(
        title=f"Organization Plan for {current_dir.resolve().name} ({len(plans)} files)",
        columns=["File", "Target Folder", "Category"],
    )
    for act in plans:
        table.add_row(act.source.name, act.category, act.category)
    console.print(table)

    if Confirm.ask("\n[bold cyan]Execute organization plan now?[/bold cyan]", default=True):
        moved = execute_organize(plans, dry_run=False)
        console.print(f"[bold green]✓ Organized {moved} files successfully![/bold green]")


def handle_workspace_menu(current_dir: Path) -> None:
    """Interactive workspace management."""
    console.print("\n[bold cyan]🌐 Workspaces Menu[/bold cyan]")
    console.print("  [bold green]1.[/bold green] List registered workspaces")
    console.print("  [bold green]2.[/bold green] Register current directory as workspace")
    console.print("  [bold dim]0.[/bold dim] Back")

    choice = Prompt.ask(
        "[bold magenta]Select option[/bold magenta]", choices=["1", "2", "0"], default="1"
    )
    if choice == "1":
        ws = list_workspaces()
        table = create_table(
            title="Registered Workspaces", columns=["Name", "Type", "Path", "Created"]
        )
        for w in ws:
            table.add_row(w.name, w.project_type, w.path, w.created_at)
        console.print(table)
    elif choice == "2":
        name = Prompt.ask(
            "[bold cyan]Workspace name[/bold cyan]", default=current_dir.resolve().name
        )
        w = add_workspace(name, current_dir)
        console.print(
            f"[bold green]✓ Registered workspace '{w.name}' [{w.project_type}][/bold green]"
        )


def handle_activity_history() -> None:
    """Interactive activity history view."""
    logs = get_activity_logs(limit=25)
    table = create_table(
        title="📜 Activity History Log",
        columns=["Timestamp", "Operation", "Target", "Status", "Details"],
    )
    for log_item in logs:
        status_style = "bold green" if log_item.result == "SUCCESS" else "bold red"
        table.add_row(
            log_item.timestamp,
            log_item.operation,
            log_item.target,
            f"[{status_style}]{log_item.result}[/{status_style}]",
            log_item.details or "-",
        )
    console.print(table)

    if Confirm.ask("\n[bold yellow]Clear all activity history?[/bold yellow]", default=False):
        clear_activity_logs()
        console.print("[bold green]✓ Activity history cleared.[/bold green]")


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


def handle_ports_menu() -> None:
    """Interactive ports inspector & killer."""
    ports = get_active_listening_ports()
    if not ports:
        console.print("[bold green]✓ No active listening ports detected on localhost.[/bold green]")
        return

    table = Table(
        title=f"Active Listening Ports ({len(ports)})",
        border_style=PALETTE["blue"],
        header_style=f"bold {PALETTE['cyan']}",
    )
    table.add_column("Port", style="bold yellow", width=8)
    table.add_column("PID", style="dim", width=8)
    table.add_column("Process Name", style=f"bold {PALETTE['green']}")
    table.add_column("Memory (MB)", style=f"{PALETTE['magenta']}", justify="right")
    table.add_column("Path", style="dim")

    for p in ports:
        table.add_row(str(p.port), str(p.pid), p.process_name, f"{p.memory_mb:.1f} MB", p.exe_path)

    console.print(table)

    kill_target = Prompt.ask(
        f"\n[{PALETTE['cyan']}]Enter port number to kill ([dim]or press Enter to skip[/dim])[/{PALETTE['cyan']}]",
        default="",
    ).strip()

    if kill_target.isdigit():
        target_port = int(kill_target)
        if Confirm.ask(
            f"[bold red]Terminate process holding port {target_port}?[/bold red]", default=True
        ):
            killed, msg = kill_port_process(target_port)
            if killed:
                console.print(f"[{PALETTE['green']}]✔ {msg}[/{PALETTE['green']}]")
            else:
                console.print(f"[{PALETTE['magenta']}]⚠ {msg}[/{PALETTE['magenta']}]")


def handle_runner_menu(current_dir: Path) -> None:
    """Interactive script runner."""
    scripts = detect_project_scripts(current_dir)
    if not scripts:
        console.print(
            "[yellow]No scripts detected in package.json, pyproject.toml, Makefile, etc.[/yellow]"
        )
        return

    table = Table(
        title=f"Available Scripts ({len(scripts)})",
        border_style=PALETTE["blue"],
        header_style=f"bold {PALETTE['cyan']}",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style=f"bold {PALETTE['green']}")
    table.add_column("Source", style=f"bold {PALETTE['magenta']}")
    table.add_column("Command", style="dim")

    for idx, s in enumerate(scripts, 1):
        table.add_row(str(idx), s.name, s.source, s.command)
    console.print(table)

    choice = Prompt.ask("Select script to execute (or Enter to cancel)", default="")
    if choice.isdigit() and 1 <= int(choice) <= len(scripts):
        s = scripts[int(choice) - 1]
        console.print(f"⚡ Running {s.name} ({s.command})...\n")
        execute_script(s.command, cwd=current_dir)


def handle_fuzzy_find(current_dir: Path) -> None:
    """Interactive fuzzy file finder."""
    query = Prompt.ask("[bold cyan]Enter file name or fuzzy search pattern[/bold cyan]", default="")
    if not query:
        return
    results = find_files_fuzzy(query, root_dir=current_dir, limit=15)
    if not results:
        console.print("[yellow]No files matched your search.[/yellow]")
        return

    table = Table(
        title=f"Matches for '{query}'",
        border_style=PALETTE["blue"],
        header_style=f"bold {PALETTE['cyan']}",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Path", style=f"bold {PALETTE['green']}")
    table.add_column("Score", style=f"{PALETTE['magenta']}", justify="right")

    for idx, r in enumerate(results, 1):
        table.add_row(str(idx), r.relative_path, f"{int(r.score)}%")
    console.print(table)

    choice = Prompt.ask("Select file # to open in editor (or Enter to exit)", default="")
    if choice.isdigit() and 1 <= int(choice) <= len(results):
        open_file_in_editor(results[int(choice) - 1].path)


def handle_notes_menu(current_dir: Path) -> None:
    """Interactive notes manager."""
    notes = list_notes(str(current_dir.resolve()))
    table = Table(
        title="Project Tasks & Scratchpad",
        border_style=PALETTE["blue"],
        header_style=f"bold {PALETTE['cyan']}",
    )
    table.add_column("ID", style="dim", width=4)
    table.add_column("Status", width=10, justify="center")
    table.add_column("Task Content", style="bold")

    for n in notes:
        st = "[green]✔ DONE[/green]" if n.status == "done" else "[yellow]⏳ TODO[/yellow]"
        cnt = f"[dim strike]{n.content}[/dim strike]" if n.status == "done" else n.content
        table.add_row(str(n.id), st, cnt)
    console.print(table)

    console.print(
        "\n[bold cyan]Options:[/bold cyan] [green][A][/green]dd Task | [green][T][/green]oggle Done | [green][D][/green]elete | [dim][Enter][/dim] Back"
    )
    opt = Prompt.ask("Action", default="").strip().upper()
    if opt == "A":
        text = Prompt.ask("Task content")
        if text:
            nid = add_note(text, str(current_dir.resolve()))
            console.print(f"[green]✔ Added task #{nid}[/green]")
    elif opt == "T":
        tid = Prompt.ask("Task ID to toggle")
        if tid.isdigit():
            _, nst = toggle_note_status(int(tid))
            console.print(f"[green]✔ Task status changed to {nst}[/green]")
    elif opt == "D":
        did = Prompt.ask("Task ID to delete")
        if did.isdigit():
            delete_note(int(did))
            console.print("[green]✔ Task deleted[/green]")


def run_interactive_dashboard(current_dir: Path) -> None:
    """Run interactive Command Center loop with action selection."""
    while True:
        console.print("\n")
        render_dashboard(current_dir)

        menu_text = Text()
        menu_text.append("  [1] ", style="bold green")
        menu_text.append("🚀 Ports Inspector & Zombie Killer (cassandra ports)\n", style="white")
        menu_text.append("  [2] ", style="bold green")
        menu_text.append("⚡ Universal Script Runner (cassandra run)\n", style="white")
        menu_text.append("  [3] ", style="bold green")
        menu_text.append("🔍 Live Fuzzy File Finder + Editor (cassandra find)\n", style="white")
        menu_text.append("  [4] ", style="bold green")
        menu_text.append("📝 Project Notes & Tasks (cassandra notes)\n", style="white")
        menu_text.append("  [5] ", style="bold green")
        menu_text.append("📁 Explore Files (List / Tree / Search / TUI)\n", style="white")
        menu_text.append("  [6] ", style="bold green")
        menu_text.append("⚒️  Create Project (DevForge Templates)\n", style="white")
        menu_text.append("  [7] ", style="bold green")
        menu_text.append("🛠️  Advanced Tools (Duplicates / Disk / Health)\n", style="white")
        menu_text.append("  [8] ", style="bold green")
        menu_text.append("📦 Organize Directory (Tidy messy files)\n", style="white")
        menu_text.append("  [9] ", style="bold green")
        menu_text.append("🌐 Workspace & Projects (Register & View)\n", style="white")
        menu_text.append("  [10] ", style="bold green")
        menu_text.append("📜 Activity History & Settings\n", style="white")
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
            choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "0"],
            default="1",
        )

        if choice == "1":
            handle_ports_menu()
        elif choice == "2":
            handle_runner_menu(current_dir)
        elif choice == "3":
            handle_fuzzy_find(current_dir)
        elif choice == "4":
            handle_notes_menu(current_dir)
        elif choice == "5":
            handle_explore_files(current_dir)
        elif choice == "6":
            handle_create_project(current_dir)
        elif choice == "7":
            handle_tools_menu(current_dir)
        elif choice == "8":
            handle_organize_files(current_dir)
        elif choice == "9":
            handle_workspace_menu(current_dir)
        elif choice == "10":
            handle_activity_history()
        elif choice == "0":
            console.print(
                "\n[bold magenta]Thank you for using CassandraID-Terminal! Goodbye 👋[/bold magenta]\n"
            )
            break

        Prompt.ask("\n[dim]Press Enter to return to main dashboard...[/dim]", default="")
