"""Dynamic UI components using Rich + pyfiglet with zoom detection."""

import os
import sys
import shutil
import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich import box
from rich.theme import Theme

# Custom theme
SHADOW_THEME = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "highlight": "bold magenta",
    "dim": "dim white",
})

console = Console(theme=SHADOW_THEME)

def clear_screen():
    """Clear terminal screen completely (no residue)."""
    # ANSI escape: clear entire screen + move cursor to 0,0
    sys.stdout.write("\033[2J\033[3J\033[H")
    sys.stdout.flush()

def get_terminal_size() -> tuple[int, int]:
    """Get terminal columns and rows."""
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except (AttributeError, ValueError, OSError):
        return 80, 24

def get_terminal_width() -> int:
    """Get terminal width."""
    cols, _ = get_terminal_size()
    return cols

def get_zoom_level() -> str:
    """Detect zoom level based on terminal width."""
    width = get_terminal_width()
    if width >= 100:
        return "large"
    elif width >= 60:
        return "medium"
    else:
        return "small"

def banner():
    """Display Shadow-SetUp banner using pyfiglet with adaptive size."""
    width = get_terminal_width()
    zoom = get_zoom_level()

    try:
        if zoom == "large":
            ascii_art = pyfiglet.figlet_format("Shadow-SetUp", font="slant")
        elif zoom == "medium":
            ascii_art = pyfiglet.figlet_format("Shadow", font="small")
        else:
            ascii_art = pyfiglet.figlet_format("SS", font="small")
    except Exception:
        ascii_art = "Shadow-SetUp"

    for line in ascii_art.rstrip().split("\n"):
        console.print(Align.center(f"[bold cyan]{line}[/bold cyan]"))

    console.print(Align.center("[dim]Modular Termux Environment Manager[/dim]"))
    console.print()

def success_box(title: str, message: str):
    """Display a success panel."""
    width = get_terminal_width()
    panel_width = min(width - 4, 80)

    console.print(Panel(
        f"[success]{message}[/success]",
        title=f"[bold green]>> {title}[/bold green]",
        border_style="green",
        box=box.ROUNDED if width >= 60 else box.SIMPLE,
        width=panel_width if width >= 60 else None,
    ))

def error_box(title: str, message: str):
    """Display an error panel."""
    width = get_terminal_width()
    panel_width = min(width - 4, 80)

    console.print(Panel(
        f"[error]{message}[/error]",
        title=f"[bold red]XX {title}[/bold red]",
        border_style="red",
        box=box.ROUNDED if width >= 60 else box.SIMPLE,
        width=panel_width if width >= 60 else None,
    ))

def info_box(title: str, message: str):
    """Display an info panel."""
    width = get_terminal_width()
    panel_width = min(width - 4, 80)

    console.print(Panel(
        f"[info]{message}[/info]",
        title=f"[bold cyan]>> {title}[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED if width >= 60 else box.SIMPLE,
        width=panel_width if width >= 60 else None,
    ))

def warning_box(title: str, message: str):
    """Display a warning panel."""
    width = get_terminal_width()
    panel_width = min(width - 4, 80)

    console.print(Panel(
        f"[warning]{message}[/warning]",
        title=f"[bold yellow]!! {title}[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED if width >= 60 else box.SIMPLE,
        width=panel_width if width >= 60 else None,
    ))

def module_table(modules: dict[str, dict]):
    """Display available modules in a table."""
    width = get_terminal_width()

    table = Table(
        title="Available Modules",
        box=box.ROUNDED if width >= 60 else box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        title_style="bold",
        expand=width >= 80,
    )

    table.add_column("Module", style="bold")
    if width >= 60:
        table.add_column("Description")
    table.add_column("Status", justify="center")

    for name, info in modules.items():
        status = "[green]+[/green]" if info.get("installed") else "[dim]-[/dim]"
        if width >= 60:
            table.add_row(name, info.get("description", ""), status)
        else:
            table.add_row(name, status)

    console.print(table)

def status_table(status_data: dict):
    """Display status information."""
    width = get_terminal_width()

    table = Table(
        title="System Status",
        box=box.ROUNDED if width >= 60 else box.SIMPLE,
        show_header=True,
        header_style="bold",
        expand=width >= 80,
    )

    table.add_column("Component", style="bold")
    table.add_column("Status")
    if width >= 60:
        table.add_column("Details")

    for component, info in status_data.items():
        status = info.get("status", "unknown")
        if status == "ok":
            status_display = "[green]+[/green]"
        elif status == "missing":
            status_display = "[red]-[/red]"
        else:
            status_display = "[yellow]?[/yellow]"

        if width >= 60:
            table.add_row(component, status_display, info.get("details", ""))
        else:
            table.add_row(component, status_display)

    console.print(table)

def interactive_menu():
    """Interactive TUI menu with arrow key navigation."""
    from InquirerPy import inquirer
    from _lib.commands import get_tui_commands, load_commands

    # Ensure commands are loaded
    load_commands()
    tui_cmds = get_tui_commands()

    # Build choices from registered commands
    choices = []
    for cmd in sorted(tui_cmds, key=lambda c: c.tui_position or 999):
        choices.append({"name": cmd.tui_label, "value": cmd.name})
    choices.append({"name": "[x] Exit", "value": "exit"})

    console.clear()
    banner()

    try:
        action = inquirer.select(
            message="What do you want to do?",
            choices=choices,
            default=choices[0]["value"] if choices else None,
        ).execute()
    except KeyboardInterrupt:
        return "exit"

    return action
