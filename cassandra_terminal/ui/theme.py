from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# Consistent Deep Space Color Palette definition
PALETTE = {
    "bg_dark": "#0A2353",
    "bg_surface": "#112C70",
    "indigo": "#5B58EB",
    "magenta": "#BB63FF",
    "cyan": "#56E1E9",
    "green": "#2ECC71",
    "yellow": "#F1C40F",
    "red": "#E74C3C",
    "blue": "#3498DB",
}

# Semantic theme matching Deep Space palette mapped for terminals
DEEP_SPACE_THEME = Theme(
    {
        "primary": "cyan",
        "primary.bold": "bold cyan",
        "secondary": "green",
        "secondary.bold": "bold green",
        "accent": "magenta",
        "accent.bold": "bold magenta",
        "warning": "yellow",
        "warning.bold": "bold yellow",
        "error": "red",
        "error.bold": "bold red",
        "muted": "dim grey70",
        "header": "bold cyan on #0A2353",
        "title": "bold magenta",
        "path": "underline cyan",
        "key": "bold magenta",
        "val": "green",
    }
)

console = Console(theme=DEEP_SPACE_THEME, safe_box=True)
error_console = Console(theme=DEEP_SPACE_THEME, stderr=True, safe_box=True)


def get_theme_header(
    title: str = "CassandraID-Terminal", subtitle: str = "Developer Intelligence Center"
) -> Panel:
    """Generate a stylized application header panel."""
    text = Text()
    text.append(" ⚡ ", style="bold cyan")
    text.append(title, style="bold cyan")
    text.append(f"  •  {subtitle}\n", style="dim magenta")
    text.append("    Local-First Developer Workspace Intelligence", style="dim")

    return Panel(
        text,
        border_style="cyan",
        padding=(0, 1),
    )


def print_banner(
    title: str = "CassandraID-Terminal", subtitle: str = "Developer Workspace Toolkit"
) -> None:
    """Print the stylized application banner."""
    console.print(get_theme_header(title, subtitle))


def create_table(title: str | None = None, columns: list[str] | None = None) -> Table:
    """Create a standardized table styled with the Deep Space theme."""
    table = Table(
        title=title,
        title_style="bold magenta",
        header_style="bold cyan",
        border_style="dim cyan",
        row_styles=["none", "dim"],
        show_header=True,
    )
    if columns:
        for col in columns:
            table.add_column(col)
    return table
