import sys
from pathlib import Path

from rich.columns import Columns
from rich.console import Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from fileforge.modules.files import FileItem, list_directory
from fileforge.ui.theme import console


def get_key() -> str:
    """Read a single keypress cross-platform without waiting for enter."""
    if sys.platform == "win32":
        import msvcrt

        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):  # Special key prefix (arrows, function keys)
            ch2 = msvcrt.getch()
            if ch2 == b"H":
                return "UP"
            if ch2 == b"P":
                return "DOWN"
            if ch2 == b"M":
                return "RIGHT"
            if ch2 == b"K":
                return "LEFT"
        if ch == b"\r":
            return "ENTER"
        if ch == b"\x08":
            return "BACKSPACE"
        if ch == b"\x1b":
            return "ESC"
        try:
            return ch.decode("utf-8", errors="ignore").lower()
        except Exception:
            return ""
    else:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                seq = sys.stdin.read(2)
                if seq == "[A":
                    return "UP"
                if seq == "[B":
                    return "DOWN"
                if seq == "[C":
                    return "RIGHT"
                if seq == "[D":
                    return "LEFT"
                return "ESC"
            if ch == "\r" or ch == "\n":
                return "ENTER"
            if ch == "\x7f":
                return "BACKSPACE"
            return ch.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def render_preview_panel(item: FileItem | None) -> Panel:
    """Render syntax highlighted or formatted content of the selected file."""
    if not item:
        return Panel(
            Text("No item selected", style="dim"), title="Preview", border_style="dim cyan"
        )

    if item.is_dir:
        # Directory Summary preview
        try:
            entries = list(item.path.iterdir())
            dir_text = Text()
            dir_text.append(f"📁 Directory: {item.name}\n", style="bold cyan")
            dir_text.append(f"Location: {item.path.resolve()}\n\n", style="dim")
            dir_text.append(f"Items count: {len(entries)}\n", style="green")
            dir_text.append("\nDirect contents:\n", style="bold magenta")
            for sub in entries[:15]:
                icon = "📁 " if sub.is_dir() else "📄 "
                dir_text.append(f"  {icon}{sub.name}\n", style="white")
            if len(entries) > 15:
                dir_text.append(f"  ... and {len(entries) - 15} more items\n", style="dim")
            return Panel(dir_text, title=f"Folder: {item.name}", border_style="magenta")
        except Exception as e:
            return Panel(
                Text(f"Cannot access folder: {e}", style="red"), title="Preview", border_style="red"
            )

    # File Preview
    ext = item.extension
    file_size_kb = item.size / 1024

    if file_size_kb > 500:
        return Panel(
            Text(
                f"File is too large for live preview ({file_size_kb:.1f} KB)\nOpen in external editor to view.",
                style="yellow",
            ),
            title=f"Preview: {item.name}",
            border_style="yellow",
        )

    try:
        content = item.path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        preview_content = "\n".join(lines[:60])  # limit first 60 lines for smooth rendering

        if ext == ".md":
            renderable = Markdown(preview_content)
        elif ext in (
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".html",
            ".css",
            ".json",
            ".toml",
            ".yaml",
            ".yml",
            ".sql",
            ".rs",
            ".go",
        ):
            lexer = ext.lstrip(".")
            if lexer in ("ts", "tsx", "jsx"):
                lexer = "javascript"
            renderable = Syntax(
                preview_content, lexer, theme="monokai", line_numbers=True, word_wrap=True
            )
        else:
            renderable = Text(preview_content, style="white")

        return Panel(
            renderable, title=f"📄 {item.name} ({item.formatted_size})", border_style="cyan"
        )
    except Exception as e:
        return Panel(
            Text(f"Unable to preview file: {e}", style="red"), title="Preview", border_style="red"
        )


def run_tui_file_browser(start_dir: Path) -> None:
    """Run full interactive TUI file explorer with dual-pane preview."""
    curr_dir = start_dir.resolve()
    selected_idx = 0

    console.clear()
    with Live(console=console, screen=True, auto_refresh=False) as live:
        while True:
            try:
                items = list_directory(curr_dir, show_hidden=False)
            except Exception:
                items = []

            if not items:
                selected_idx = 0
            else:
                selected_idx = max(0, min(selected_idx, len(items) - 1))

            selected_item = items[selected_idx] if items else None

            # 1. Left List Table
            list_table = Table(
                title=f"📁 {curr_dir}",
                title_style="bold cyan",
                border_style="dim cyan",
                show_header=True,
                expand=True,
            )
            list_table.add_column("Sel", width=3, style="bold magenta")
            list_table.add_column("Type", width=6)
            list_table.add_column("Name", style="white")
            list_table.add_column("Size", width=10, justify="right", style="dim")

            # Show window around selected index
            max_visible = 18
            start_row = max(0, selected_idx - (max_visible // 2))
            end_row = min(len(items), start_row + max_visible)

            for idx in range(start_row, end_row):
                it = items[idx]
                is_selected = idx == selected_idx
                sel_marker = "▶ " if is_selected else "  "
                type_icon = (
                    "[bold magenta]DIR [/bold magenta]" if it.is_dir else "[cyan]FILE[/cyan]"
                )
                name_style = (
                    "bold cyan on #112C70"
                    if is_selected
                    else ("bold magenta" if it.is_dir else "white")
                )
                list_table.add_row(
                    sel_marker,
                    type_icon,
                    f"[{name_style}]{it.name}[/{name_style}]",
                    it.formatted_size,
                )

            left_panel = Panel(list_table, title="Explorer", border_style="cyan")

            # 2. Right Preview Panel
            right_panel = render_preview_panel(selected_item)

            # 3. Bottom Hotkey Help
            help_text = Text()
            help_text.append(" [↑/k] ", style="bold cyan")
            help_text.append("Up  ", style="dim")
            help_text.append("[↓/j] ", style="bold cyan")
            help_text.append("Down  ", style="dim")
            help_text.append("[Enter/→/l] ", style="bold green")
            help_text.append("Open folder  ", style="dim")
            help_text.append("[Backspace/←/h] ", style="bold yellow")
            help_text.append("Parent folder  ", style="dim")
            help_text.append("[q] ", style="bold red")
            help_text.append("Exit TUI", style="dim")

            bottom_panel = Panel(help_text, border_style="dim magenta", padding=(0, 1))

            layout_group = Group(
                Columns([left_panel, right_panel], equal=True),
                bottom_panel,
            )

            live.update(layout_group, refresh=True)

            # Handle Key Input
            key = get_key()
            if key in ("q", "ESC"):
                break
            elif key in ("UP", "k"):
                selected_idx = max(0, selected_idx - 1)
            elif key in ("DOWN", "j"):
                if items:
                    selected_idx = min(len(items) - 1, selected_idx + 1)
            elif key in ("ENTER", "RIGHT", "l"):
                if selected_item and selected_item.is_dir:
                    curr_dir = selected_item.path
                    selected_idx = 0
            elif key in ("BACKSPACE", "LEFT", "h"):
                if curr_dir.parent != curr_dir:
                    curr_dir = curr_dir.parent
                    selected_idx = 0
