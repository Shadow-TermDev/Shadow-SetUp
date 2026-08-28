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

    def execute(self, args=None):
        from _lib.utils.ui import console, banner, status_table
        from _lib.modules.loader import load_modules
        from _lib.commands import get_all_commands

        modules = load_modules()
        commands = get_all_commands()

        banner()
        console.print("[bold]Usage:[bold] [cyan]sw[/cyan] [command]")
        console.print()

        # Commands
        console.print("[bold]Commands:[bold]")
        for cmd in commands:
            aliases = f" [dim]({', '.join(cmd.aliases)})[/dim]" if cmd.aliases else ""
            console.print(f"  [cyan]{cmd.name}[/cyan]{aliases} — {cmd.description}")
        console.print()

        # Modules
        console.print("[bold]Modules:[bold]")
        for name, mod in sorted(modules.items()):
            status = mod.status()
            installed = "[green]+[/green]" if status.get("status") == "ok" else "[dim]-[/dim]"
            console.print(f"  {installed} [cyan]{name}[/cyan] — {mod.description}")
        console.print()

        # RICE
        console.print("[bold]RICE:[bold]")
        rice_cmds = [c for c in commands if c.name == "rice"]
        console.print("  [cyan]rice list[/cyan]      List available RICEs")
        console.print("  [cyan]rice set[/cyan]       Set active RICE")
        console.print("  [cyan]rice check[/cyan]     Show active RICE")
        console.print("  [cyan]rice install[/cyan]   Install RICE from git")
        console.print()

        # Examples
        console.print("[bold]Examples:[bold]")
        console.print("  [dim]sw[/dim]                     Interactive menu")
        console.print("  [dim]sw install shell[/dim]       Install zsh + plugins")
        console.print("  [dim]sw update[/dim]              Update all modules")
        console.print("  [dim]sw status[/dim]              Show all status")
        console.print("  [dim]sw rice set kawaii[/dim]     Activate kawaii RICE")
        console.print()
        console.print("[dim]Shadow-TermDev · https://Shadow-TermDev.github.io[/dim]")
