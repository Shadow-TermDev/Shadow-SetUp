"""Dynamic UI components using Rich with zoom detection."""

import os
import sys
import shutil
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

# Custom logo art — compact and clean
LOGO_LARGE = """[bold cyan]         ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗[/bold cyan]
[bold cyan]         ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║[/bold cyan]
[bold cyan]         ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║[/bold cyan]
[bold cyan]         ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║[/bold cyan]
[bold cyan]         ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝[/bold cyan]
[bold cyan]         ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝[/bold cyan]"""

LOGO_MEDIUM = """[bold cyan]        ╔═╗╦ ╦╦═╗╔═╗╔╦╗╔═╗╔═╗╔╦╗[/bold cyan]
[bold cyan]        ║  ║ ║╠╦╝╠═╣ ║ ║╣ ╚═╗ ║[/bold cyan]
[bold cyan]        ╚═╝╚═╝╩╚═╩ ╩ ╩ ╚═╝╚═╝ ╩[/bold cyan]"""

LOGO_SMALL = "[bold cyan]🖤 Shadow-SetUp[/bold cyan]"

def banner():
    """Display Shadow-SetUp banner with adaptive size."""
    width = get_terminal_width()
    zoom = get_zoom_level()
    
    if zoom == "large":
        logo = LOGO_LARGE
    elif zoom == "medium":
        logo = LOGO_MEDIUM
    else:
        logo = LOGO_SMALL
    
    for line in logo.split("\n"):
        console.print(Align.center(line))
    
    console.print(Align.center("[dim]Modular Termux Environment Manager[/dim]"))
    console.print()

def success_box(title: str, message: str):
    """Display a success panel."""
    width = get_terminal_width()
    panel_width = min(width - 4, 80)
    
    console.print(Panel(
        f"[success]{message}[/success]",
        title=f"[bold green]✓ {title}[/bold green]",
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
        title=f"[bold red]✗ {title}[/bold red]",
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
        title=f"[bold cyan]→ {title}[/bold cyan]",
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
        title=f"[bold yellow]! {title}[/bold yellow]",
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
        status = "[green]✓[/green]" if info.get("installed") else "[dim]○[/dim]"
        if width >= 60:
            table.add_row(name, info.get("description", ""), status)
        else:
            table.add_row(name, status)
    
    console.print(table)

def progress_bar(current: int, total: int, label: str = ""):
    """Display a dynamic progress bar."""
    width = get_terminal_width()
    bar_width = min(width - 40, 50)
    filled = int(bar_width * current / total)
    bar = "█" * filled + "░" * (bar_width - filled)
    percent = current * 100 // total
    
    console.print(f"\r  {label} [{bar}] {percent}%", end="", refresh=True)
    if current == total:
        console.print()

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
            status_display = "[green]✓ Installed[/green]"
        elif status == "missing":
            status_display = "[red]✗ Missing[/red]"
        else:
            status_display = "[yellow]? Unknown[/yellow]"
        
        if width >= 60:
            table.add_row(component, status_display, info.get("details", ""))
        else:
            table.add_row(component, status_display)
    
    console.print(table)

def clear_screen():
    """Clear terminal screen."""
    console.clear()
