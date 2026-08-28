"""Help command — show help info."""

from _lib.commands import Command

class HelpCommand(Command):
    name = "help"
    aliases = ["--help", "-h"]
    description = "Show help information"
    usage = "help"
    examples = ["help             # Show all commands"]
    tui_label = None  # Not in TUI
    tui_position = 99
    tui_section = None

    def execute(self, args: list[str] = None) -> None:
        from _lib.utils.ui import console, banner, module_table
        from _lib.modules.loader import load_modules
        from _lib.commands import get_all_commands

        modules = load_modules()
        commands = get_all_commands()

        banner()
        console.print("[bold]Usage:[bold] sw [command]")
        console.print()
        console.print("[bold]Commands:[bold]")
        for cmd in commands:
            console.print(f"  [cyan]{cmd.name}[/cyan] {cmd.description}")
        console.print()
        console.print("[bold]Modules:[bold]")
        for name, mod in sorted(modules.items()):
            console.print(f"  [cyan]{name}[/cyan] — {mod.description}")
        console.print()
        console.print("[bold]RICE:[bold]")
        console.print("  [cyan]rice list[/cyan]      List available RICEs")
        console.print("  [cyan]rice set[/cyan]       Set active RICE")
        console.print("  [cyan]rice install[/cyan]   Install RICE from git")
        console.print("  [cyan]rice check[/cyan]     Show active RICE")
        console.print()
        console.print("[bold]Examples:[bold]")
        console.print("  sw                     # Interactive menu")
        console.print("  sw install shell       # Install zsh + plugins")
        console.print("  sw update              # Update all modules")
        console.print("  sw status              # Show all status")
        console.print("  sw rice set kawaii     # Activate kawaii RICE")
        console.print()
        console.print("[dim]Shadow-TermDev · https://Shadow-TermDev.github.io[/dim]")
