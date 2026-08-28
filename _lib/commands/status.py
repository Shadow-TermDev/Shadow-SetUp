"""Status command — show module status."""

from _lib.commands import Command

class StatusCommand(Command):
    name = "status"
    aliases = ["st"]
    description = "Show module status"
    usage = "status [module]"
    examples = [
        "status                 # Show all status",
        "status shell           # Show shell status",
    ]
    tui_label = "[5] System status"
    tui_position = 50
    tui_section = "main"

    def execute(self, args: list[str] = None) -> None:
        from _lib.utils.ui import banner, status_box, error_box
        from _lib.modules.loader import load_modules

        modules = load_modules()
        banner()

        if not args:
            for name, mod in sorted(modules.items()):
                status = mod.status()
                status_box(name, status)
        else:
            for name in args:
                if name in modules:
                    status = modules[name].status()
                    status_box(name, status)
                else:
                    error_box("Module", f"'{name}' not found")
