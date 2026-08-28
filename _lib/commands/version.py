"""Version command — show version info."""

from _lib.commands import Command

class VersionCommand(Command):
    name = "version"
    aliases = ["v", "--version"]
    description = "Show version info"
    usage = "version"
    examples = ["version          # Show version", "v                # Short form"]
    tui_label = "[8] Version info"
    tui_position = 80
    tui_section = "main"

    def execute(self, args: list[str] = None) -> None:
        from _lib.utils.ui import console, banner
        from _lib import __version__
        banner()
        console.print(f"Shadow-SetUp v{__version__}")
