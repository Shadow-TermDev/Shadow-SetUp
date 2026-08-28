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

    def execute(self, args=None):
        from _lib.utils.ui import banner, status_table, error_box
        from _lib.modules.loader import load_modules

        if args is None:
            args = []

        modules = load_modules()
        banner()

        if not args:
            status_data = {}
            for name, mod in sorted(modules.items()):
                status = mod.status()
                status_data[name] = {
                    "description": mod.description,
                    "status": status.get("status", "unknown"),
                    "details": status.get("details", "")
                }
            status_table(status_data)
        else:
            for name in args:
                if name in modules:
                    status = modules[name].status()
                    print(f"\n{name}: {status}")
                else:
                    error_box("Module", f"'{name}' not found")
