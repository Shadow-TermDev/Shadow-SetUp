"""List command — list available modules."""

from _lib.commands import Command

class ListCommand(Command):
    name = "list"
    aliases = ["ls"]
    description = "List available modules"
    usage = "list"
    examples = ["list               # Show all modules"]
    tui_label = "[4] List modules"
    tui_position = 40
    tui_section = "main"

    def execute(self, args: list[str] = None) -> None:
        from _lib.utils.ui import banner, module_table
        from _lib.modules.loader import load_modules

        modules = load_modules()
        banner()
        modules_info = {}
        for name, mod in sorted(modules.items()):
            status = mod.status()
            modules_info[name] = {
                "description": mod.description,
                "installed": status.get("status") == "ok"
            }
        module_table(modules_info)
