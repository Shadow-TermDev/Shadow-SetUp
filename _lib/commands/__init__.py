"""Command system — dynamic command loading and registry."""

import pkgutil
import importlib
from pathlib import Path
from dataclasses import dataclass, field
from types import SimpleNamespace

@dataclass
class Command:
    """Command metadata for dispatch, help, and TUI generation."""
    name: str                                    # Primary name (e.g., "version")
    aliases: list[str] = field(default_factory=list)  # Alt names (e.g., ["v"])
    description: str = ""                        # What it does
    usage: str = ""                              # Usage string
    examples: list[str] = field(default_factory=list)  # Example usage
    tui_label: str | None = None                 # Label in TUI (None = not in TUI)
    tui_position: int | None = None              # Position in TUI menu
    tui_section: str | None = None               # "main" or "rice" submenu
    needs_args: bool = False                     # Requires arguments?
    has_submenu: bool = False                    # Has submenu in TUI?
    handler: str = ""                            # Module path to import
    handler_func: str = ""                       # Function name to call (empty = use name)

    def matches(self, arg: str) -> bool:
        """Check if a CLI argument matches this command."""
        return arg == self.name or arg in self.aliases

    def execute(self, args: list[str] = None) -> None:
        """Execute the command (override in subclass)."""
        pass

# Command registry — populated by load_commands()
COMMANDS: list[Command] = []

_COMMANDS_DIR = Path(__file__).parent

def _make_command(cls) -> Command:
    """Create a Command instance from a class with class-level attributes."""
    import types
    
    cmd = Command.__new__(Command)
    cmd.name = getattr(cls, 'name', '')
    cmd.aliases = getattr(cls, 'aliases', [])
    cmd.description = getattr(cls, 'description', '')
    cmd.usage = getattr(cls, 'usage', '')
    cmd.examples = getattr(cls, 'examples', [])
    cmd.tui_label = getattr(cls, 'tui_label', None)
    cmd.tui_position = getattr(cls, 'tui_position', None)
    cmd.tui_section = getattr(cls, 'tui_section', None)
    cmd.needs_args = getattr(cls, 'needs_args', False)
    cmd.has_submenu = getattr(cls, 'has_submenu', False)
    cmd.handler = getattr(cls, 'handler', '')
    cmd.handler_func = getattr(cls, 'handler_func', '')
    cmd.subcommands = getattr(cls, 'subcommands', None)
    
    # Bind ALL methods from the subclass (including private methods)
    for attr_name in dir(cls):
        if attr_name.startswith('__'):
            continue
        attr = getattr(cls, attr_name)
        if callable(attr) and attr_name not in ('name', 'aliases', 'description', 'usage', 'examples', 'tui_label', 'tui_position', 'tui_section', 'needs_args', 'has_submenu', 'handler', 'handler_func', 'subcommands'):
            # Create a bound method
            bound = types.MethodType(attr, cmd)
            setattr(cmd, attr_name, bound)
    
    return cmd

def load_commands() -> list[Command]:
    """Auto-discover and instantiate all Command subclasses in _lib/commands/."""
    global COMMANDS
    commands = []

    for importer, modname, ispkg in pkgutil.iter_modules([str(_COMMANDS_DIR)]):
        if modname.startswith("_") or modname == "base":
            continue

        try:
            full_name = f"_lib.commands.{modname}"
            mod = importlib.import_module(full_name)

            # Find the class that inherits from Command
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, Command)
                    and attr is not Command
                    and hasattr(attr, "name")
                ):
                    cmd = _make_command(attr)
                    commands.append(cmd)
                    break

        except Exception as e:
            import warnings
            warnings.warn(f"Failed to load command '{modname}': {e}", stacklevel=2)

    # Sort by tui_position
    commands.sort(key=lambda c: c.tui_position or 999)
    COMMANDS = commands
    return commands

def get_command(arg: str) -> Command | None:
    """Get a command by name or alias."""
    for cmd in COMMANDS:
        if cmd.matches(arg):
            return cmd
    return None

def get_all_commands() -> list[Command]:
    """Get all registered commands."""
    return COMMANDS

def get_tui_commands() -> list[Command]:
    """Get commands that appear in the TUI main menu."""
    return [c for c in COMMANDS if c.tui_label and c.tui_section == "main"]

def get_rice_commands() -> list[Command]:
    """Get commands that appear in the RICE submenu."""
    return [c for c in COMMANDS if c.tui_label and c.tui_section == "rice"]
