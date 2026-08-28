"""Install command — install a module."""

from _lib.commands import Command

class InstallCommand(Command):
    name = "install"
    aliases = ["i"]
    description = "Install a module"
    usage = "install <module>"
    examples = [
        "install shell          # Install zsh + plugins",
        "install shell tools    # Install multiple modules",
    ]
    tui_label = "[1] Install module"
    tui_position = 10
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
                    message="Select modules to install:",
                    choices=choices,
                ).execute()
                if not selected or "[cancel]" in selected:
                    return
                args = [s for s in selected if s != "[cancel]"]
            except (KeyboardInterrupt, EOFError):
                return

        if not args:
            error_box("Error", "Usage: install <module> [module2] ...")
            return

        banner()
        for name in args:
            if name in modules:
                console.print(f"\n[bold cyan]Installing {name}...[/bold cyan]")
                success = modules[name].install()
                if success:
                    success_box("Module", f"{name} installed")
                else:
                    error_box("Module", f"{name} failed")
            else:
                error_box("Module", f"'{name}' not found")
