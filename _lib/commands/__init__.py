"""Command registry — dynamic command loading."""

import importlib
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Command:
    name: str
    description: str
    usage: str
    examples: list[str]
    module: str  # module path to import

COMMANDS: list[Command] = [
    Command(
        name="install",
        description="Install a module",
        usage="install <module>",
        examples=[
            "install shell          # Install zsh + plugins",
            "install shell tools    # Install multiple modules",
        ],
        module="install",
    ),
    Command(
        name="update",
        description="Update module(s)",
        usage="update [module]",
        examples=[
            "update                 # Update all modules",
            "update shell           # Update only shell",
        ],
        module="update",
    ),
    Command(
        name="uninstall",
        description="Uninstall a module",
        usage="uninstall <module>",
        examples=[
            "uninstall shell        # Remove shell config",
        ],
        module="uninstall",
    ),
    Command(
        name="list",
        description="List available modules",
        usage="list",
        examples=[],
        module="list",
    ),
    Command(
        name="status",
        description="Show module status",
        usage="status [module]",
        examples=[
            "status                 # Show all status",
            "status shell           # Show shell status",
        ],
        module="status",
    ),
    Command(
        name="update-core",
        description="Update framework from GitHub",
        usage="update-core",
        examples=[],
        module="update_core",
    ),
    Command(
        name="version",
        description="Show version info",
        usage="version",
        examples=[],
        module="version",
    ),
]

def get_command(name: str) -> Command | None:
    """Get a command by name."""
    for cmd in COMMANDS:
        if cmd.name == name:
            return cmd
    return None

def get_all_commands() -> list[Command]:
    """Get all registered commands."""
    return COMMANDS
