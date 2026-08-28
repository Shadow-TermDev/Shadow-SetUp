"""Update command — update module(s)."""

from _lib.commands import Command

class UpdateCommand(Command):
    name = "update"
    aliases = ["u"]
    description = "Update module(s)"
    usage = "update [module]"
    examples = [
        "update                 # Update all modules",
        "update shell           # Update only shell",
    ]
    tui_label = "[2] Update modules"
    tui_position = 20
    tui_section = "main"

    def execute(self, args=None):
        from _lib.utils.ui import console, banner, success_box, error_box
        from _lib.modules.loader import load_modules

        if args is None:
            args = []

        modules = load_modules()

        # If no args from TUI, show module selector
        if not args:
            try:
                from InquirerPy import inquirer
                choices = sorted(modules.keys()) + ["all", "[cancel]"]
                selected = inquirer.checkbox(
                    message="Select modules to update:",
                    choices=choices,
                ).execute()
                if not selected or "[cancel]" in selected:
                    return
                if "all" in selected:
                    args = []  # Empty = update all
                else:
                    args = [s for s in selected if s != "all"]
            except (KeyboardInterrupt, EOFError):
                return

        banner()

        try:
            if not args:
                # Update all
                for name, mod in sorted(modules.items()):
                    console.print(f"\n[bold cyan]Updating {name}...[/bold cyan]")
                    success = mod.update()
                    if success:
                        success_box("Module", f"{name} updated")
                    else:
                        error_box("Module", f"{name} failed")
            else:
                # Update specified
                for name in args:
                    if name in modules:
                        console.print(f"\n[bold cyan]Updating {name}...[/bold cyan]")
                        success = modules[name].update()
                        if success:
                            success_box("Module", f"{name} updated")
                        else:
                            error_box("Module", f"{name} failed")
                    else:
                        error_box("Module", f"'{name}' not found")
        except KeyboardInterrupt:
            console.print("\n[dim]Cancelled[/dim]")
