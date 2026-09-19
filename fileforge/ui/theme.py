from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

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


def print_banner(
    title: str = "FileForge DevKit", subtitle: str = "Developer Workspace Toolkit"
) -> None:
    """Print the stylized application banner."""
    text = Text()
    text.append(" 🗂️  ", style="bold magenta")
    text.append(title, style="bold cyan")
    text.append(f"  •  {subtitle}\n", style="dim cyan")
    text.append("    Local-First • Terminal Intelligence • Project Scaffolding", style="dim")

    panel = Panel(
        text,
        border_style="cyan",
        padding=(0, 1),
    )
    console.print(panel)


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
