"""Uninstall command — uninstall a module."""

from _lib.commands import Command

class UninstallCommand(Command):
    name = "uninstall"
    aliases = ["rm"]
    description = "Uninstall a module"
    usage = "uninstall <module>"
    examples = [
        "uninstall shell        # Remove shell config",
    ]
    tui_label = "[3] Uninstall module"
    tui_position = 30
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
                choices = sorted(modules.keys()) + ["[cancel]"]
                selected = inquirer.checkbox(
                    message="Select modules to uninstall:",
                    choices=choices,
                ).execute()
                if not selected or "[cancel]" in selected:
                    return
                args = [s for s in selected if s != "[cancel]"]
            except (KeyboardInterrupt, EOFError):
                return

        if not args:
            error_box("Error", "Usage: uninstall <module>")
            return

        banner()
        for name in args:
            if name in modules:
                console.print(f"\n[bold cyan]Uninstalling {name}...[/bold cyan]")
                success = modules[name].uninstall()
                if success:
                    success_box("Module", f"{name} uninstalled")
                else:
                    error_box("Module", f"{name} failed")
            else:
                error_box("Module", f"'{name}' not found")
