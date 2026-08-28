#!/usr/bin/env python3
"""
Shadow-SetUp CLI — Modular Termux Environment Manager.

Usage:
    sw              Interactive menu (TUI)
    sw <command>    Run a command
    sw -h, --help   Show help
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for both installed and dev modes
lib_dir = Path(__file__).parent
sys.path.insert(0, str(lib_dir.parent))
sys.path.insert(0, str(lib_dir))

from _lib import __version__
from _lib.utils.ui import (
    console, banner, interactive_menu,
    clear_screen
)
from _lib.utils import ensure_dirs
from _lib.commands import load_commands, get_command, get_all_commands

# Dynamic command loading
COMMANDS = load_commands()

def run_interactive():
    """Run interactive TUI menu."""
    from InquirerPy import inquirer
    from _lib.utils.rice_manager import get_active_rice

    while True:
        try:
            action = interactive_menu()

            if action == "exit":
                console.print("[dim]Bye![/dim]")
                break

            clear_screen()

            # Find and execute the command
            cmd = get_command(action)
            if cmd and cmd.has_submenu:
                _handle_submenu(cmd)
            elif cmd:
                cmd.execute()
            else:
                console.print(f"[red]Unknown command: {action}[/red]")

            # Pause before returning to menu
            if action != "exit":
                console.print()
                input("Press Enter to continue...")

        except KeyboardInterrupt:
            console.print("\n[dim]Cancelled[/dim]")
            continue
        except EOFError:
            console.print("\n[dim]Bye![/dim]")
            break

def _handle_submenu(cmd):
    """Handle commands with submenus (e.g., rice)."""
    from InquirerPy import inquirer
    from _lib.commands import get_rice_commands

    if cmd.name == "rice":
        rice_choices = [
            {"name": "[1] Check active RICE", "value": "check"},
            {"name": "[2] List RICEs", "value": "list"},
            {"name": "[3] Set/Download RICE", "value": "set"},
            {"name": "[4] Install from git URL", "value": "install"},
            {"name": "[5] Delete local RICE", "value": "delete"},
            {"name": "[6] Backup current", "value": "backup"},
            {"name": "[x] Back", "value": "back"},
        ]

        rice_action = inquirer.select(
            message="RICE manager:",
            choices=rice_choices,
        ).execute()

        if rice_action == "back":
            return

        if rice_action == "set":
            from _lib.utils.rice_manager import fetch_official_rices
            official = fetch_official_rices()
            rice_names = list(official.keys()) + ["[cancel]"]
            selected = inquirer.select(
                message="Select RICE to activate:",
                choices=rice_names,
            ).execute()
            if selected and selected != "[cancel]":
                cmd.execute(["set", selected])
        elif rice_action == "install":
            url = inquirer.text(message="Git URL:").execute()
            if url:
                cmd.execute(["install", url])
        elif rice_action == "delete":
            from _lib.utils.rice_manager import list_local_rices
            local = list_local_rices()
            if local:
                names = [r["name"] for r in local] + ["[cancel]"]
                selected = inquirer.select(
                    message="Select RICE to delete:",
                    choices=names,
                ).execute()
                if selected and selected != "[cancel]":
                    cmd.execute(["delete", selected])
            else:
                from _lib.utils.ui import info_box
                info_box("RICEs", "No local RICEs to delete")
        elif rice_action == "backup":
            from _lib.utils.rice_manager import get_active_rice
            active = get_active_rice()
            if active:
                cmd.execute(["backup", active])
            else:
                from _lib.utils.ui import info_box
                info_box("RICEs", "No active RICE to backup")
        else:
            cmd.execute([rice_action])

def main():
    """Main entry point."""
    ensure_dirs()

    args = sys.argv[1:]

    # No args = interactive mode
    if not args:
        run_interactive()
        return

    command = args[0]
    cmd_args = args[1:]

    # Find command
    cmd = get_command(command)

    if not cmd:
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print("Run 'sw help' for usage info.")
        sys.exit(1)

    # Check if command needs args
    if cmd.needs_args and not cmd_args:
        console.print(f"[red]Usage: {cmd.usage}[/red]")
        sys.exit(1)

    # Commands that need banner
    NEEDS_BANNER = {"list", "install", "update", "uninstall", "status", "update-core", "rice"}
    if cmd.name in NEEDS_BANNER:
        clear_screen()

    # Execute
    cmd.execute(cmd_args)

if __name__ == "__main__":
    main()
