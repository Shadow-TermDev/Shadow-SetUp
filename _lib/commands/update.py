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

    def execute(self, args: list[str] = None) -> None:
        from _lib.utils.ui import console, banner, success_box, error_box
        from _lib.modules.loader import load_modules

        modules = load_modules()

        banner()

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
