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
        from _lib.utils.ui import console, success_box, error_box, info_box
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

        console.print()
        for name in args:
            if name not in modules:
                error_box("Module", f"'{name}' not found")
                continue

            mod = modules[name]
            status = mod.status()
            is_installed = status.get("status") == "ok"

            if not is_installed:
                info_box("Module", f"{name} not installed — skipping")
                continue

            console.print(f"\n[bold cyan]Uninstalling {name}...[/bold cyan]")
            success = mod.uninstall()
            if success:
                success_box("Module", f"{name} uninstalled")
            else:
                error_box("Module", f"{name} failed")
