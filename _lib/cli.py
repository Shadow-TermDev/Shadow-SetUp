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
    console, banner, success_box, error_box,
    info_box, module_table, status_table, interactive_menu
)
from _lib.utils import SHADOW_DATA, ensure_dirs
from _lib.modules.loader import load_modules

# Dynamic module loading
MODULES = load_modules()

def show_help():
    """Display help information."""
    banner()
    console.print("[bold]Usage:[/bold] sw [command]")
    console.print()
    console.print("[bold]Commands:[/bold]")
    console.print("  [cyan]install[reset]        Install a module")
    console.print("  [cyan]update[reset]         Update module(s)")
    console.print("  [cyan]uninstall[reset]      Uninstall a module")
    console.print("  [cyan]list[reset]           List available modules")
    console.print("  [cyan]status[reset]         Show module status")
    console.print("  [cyan]rice[reset]           Manage RICE themes")
    console.print("  [cyan]update-core[reset]    Update framework from GitHub")
    console.print("  [cyan]version[reset]        Show version info")
    console.print()
    console.print("[bold]Modules:[/bold]")
    for name, mod in sorted(MODULES.items()):
        console.print(f"  [cyan]{name}[/cyan] — {mod.description}")
    console.print()
    console.print("[bold]RICE:[/bold]")
    console.print("  [cyan]rice list[reset]      List available RICEs")
    console.print("  [cyan]rice set[reset]       Set active RICE")
    console.print("  [cyan]rice install[reset]   Install RICE from git")
    console.print()
    console.print("[bold]Examples:[/bold]")
    console.print("  sw                     # Interactive menu")
    console.print("  sw install shell       # Install zsh + plugins")
    console.print("  sw update              # Update all modules")
    console.print("  sw status              # Show all status")
    console.print("  sw rice set kawaii     # Activate kawaii RICE")
    console.print()
    console.print("[dim]Shadow-TermDev · https://Shadow-TermDev.github.io[/dim]")

def list_modules():
    """List all available modules."""
    banner()
    modules_info = {}
    for name, mod in sorted(MODULES.items()):
        status = mod.status()
        modules_info[name] = {
            "description": mod.description,
            "installed": status.get("status") == "ok"
        }
    module_table(modules_info)

def install_modules(module_names: list[str]):
    """Install specified modules."""
    banner()
    for name in module_names:
        if name not in MODULES:
            error_box("Error", f"Unknown module: {name}")
            continue
        MODULES[name].install()
        console.print()

def update_modules(module_names: list[str] = None):
    """Update modules (all if none specified)."""
    banner()
    targets = module_names if module_names else list(MODULES.keys())
    for name in targets:
        if name not in MODULES:
            error_box("Error", f"Unknown module: {name}")
            continue
        MODULES[name].update()
        console.print()

def uninstall_modules(module_names: list[str]):
    """Uninstall specified modules."""
    banner()
    for name in module_names:
        if name not in MODULES:
            error_box("Error", f"Unknown module: {name}")
            continue
        MODULES[name].uninstall()
        console.print()

def show_status(module_names: list[str] = None):
    """Show status of modules."""
    banner()
    if module_names:
        for name in module_names:
            if name not in MODULES:
                error_box("Error", f"Unknown module: {name}")
                continue
            status = MODULES[name].status()
            console.print(f"  [bold]{name}:[/bold] {status.get('details', 'unknown')}")
    else:
        status_data = {}
        for name, mod in sorted(MODULES.items()):
            status = mod.status()
            status_data[name] = {
                "status": "ok" if status.get("status") == "ok" else "missing",
                "details": status.get("details", "")
            }
        status_table(status_data)

def update_core():
    """Update Shadow-SetUp from GitHub."""
    import subprocess
    import shutil

    banner()

    temp_dir = SHADOW_DATA / "cache" / "shadow-update"

    with console.status("[bold cyan]Downloading update...[/bold cyan]", spinner="dots") as status:
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

            result = subprocess.run([
                "git", "clone", "--depth=1",
                "https://github.com/Shadow-TermDev/Shadow-SetUp.git",
                str(temp_dir)
            ], capture_output=True, text=True)

            if result.returncode != 0:
                error_box("Update failed", "Could not download update")
                return

            status.update("[bold cyan]Installing files...[/bold cyan]")

            # Copy _lib
            lib_src = temp_dir / "_lib"
            lib_dst = SHADOW_DATA / "_lib"
            if lib_src.exists():
                if lib_dst.exists():
                    shutil.rmtree(lib_dst)
                shutil.copytree(lib_src, lib_dst)

            # Copy dotfiles
            dotfiles_src = temp_dir / "dotfiles"
            dotfiles_dst = SHADOW_DATA / "dotfiles"
            if dotfiles_src.exists():
                if dotfiles_dst.exists():
                    shutil.rmtree(dotfiles_dst)
                shutil.copytree(dotfiles_src, dotfiles_dst)

            # Copy .version
            version_src = temp_dir / ".version"
            version_dst = SHADOW_DATA / ".version"
            if version_src.exists():
                shutil.copy2(version_src, version_dst)

            # Update wrappers
            bin_dir = Path.home() / ".local" / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)

            for cmd_name in ["sw", "shadow"]:
                wrapper = bin_dir / cmd_name
                wrapper.write_text(f"""#!/data/data/com.termux/files/usr/bin/bash
exec python3 "{SHADOW_DATA}/_lib/cli.py" "$@"
""")
                wrapper.chmod(0o755)

            shutil.rmtree(temp_dir)

        except Exception as e:
            error_box("Update failed", str(e))
            return

    success_box("Update complete!", "Shadow-SetUp is now up to date")

# RICE commands
def rice_list():
    """List available RICEs (official + local)."""
    from _lib.utils.rice_manager import fetch_official_rices, list_local_rices, get_active_rice

    banner()
    official = fetch_official_rices()
    local = list_local_rices()
    local_names = {r["name"] for r in local}
    active = get_active_rice()

    console.print("[bold]Official RICEs:[/bold]")
    for name, info in sorted(official.items()):
        installed = " [dim]+installed[/dim]" if name in local_names else ""
        marker = " [green]*[/green]" if name == active else ""
        console.print(f"  [cyan]{name}[/cyan]{marker}{installed} — {info.get('description', '')}")

    if local:
        console.print()
        console.print("[bold]Local RICEs:[/bold]")
        for rice in local:
            if rice["name"] not in official:
                marker = " [green]*[/green]" if rice["name"] == active else ""
                console.print(f"  [cyan]{rice['name']}[/cyan]{marker}")

    console.print()
    console.print("[dim]* = active | + = downloaded[/dim]")

def rice_set(rice_name: str):
    """Download (if needed) and activate a RICE."""
    from _lib.utils.rice_manager import download_and_apply_rice
    banner()
    download_and_apply_rice(rice_name)

def rice_install(url: str):
    """Install a custom RICE from git URL."""
    from _lib.utils.rice_manager import install_custom_rice
    banner()
    install_custom_rice(url)

def rice_delete(rice_name: str):
    """Delete a local RICE."""
    from _lib.utils.rice_manager import delete_rice
    banner()
    delete_rice(rice_name)

def rice_backup(rice_name: str):
    """Backup current RICE."""
    from _lib.utils.rice_manager import backup_current_rice
    banner()
    backup_current_rice(rice_name)

def handle_rice(args: list[str]):
    """Handle rice subcommands."""
    if not args or args[0] == "list":
        rice_list()
    elif args[0] == "set" and len(args) > 1:
        rice_set(args[1])
    elif args[0] == "install" and len(args) > 1:
        rice_install(args[1])
    elif args[0] == "delete" and len(args) > 1:
        rice_delete(args[1])
    elif args[0] == "backup" and len(args) > 1:
        rice_backup(args[1])
    else:
        error_box("Error", "Usage: rice [list|set|install|delete|backup] [args]")

def run_interactive():
    """Run interactive TUI menu."""
    from InquirerPy import inquirer

    while True:
        try:
            action = interactive_menu()

            if action == "exit":
                console.print("[dim]Bye![/dim]")
                break

            console.clear()

            if action == "install":
                choices = sorted(MODULES.keys()) + ["[cancel]"]
                selected = inquirer.checkbox(
                    message="Select modules to install:",
                    choices=choices,
                ).execute()
                if selected and "[cancel]" not in selected:
                    install_modules(selected)

            elif action == "update":
                choices = sorted(MODULES.keys()) + ["all", "[cancel]"]
                selected = inquirer.checkbox(
                    message="Select modules to update:",
                    choices=choices,
                ).execute()
                if selected and "[cancel]" not in selected:
                    if "all" in selected:
                        update_modules()
                    else:
                        update_modules(selected)

            elif action == "uninstall":
                choices = sorted(MODULES.keys()) + ["[cancel]"]
                selected = inquirer.checkbox(
                    message="Select modules to uninstall:",
                    choices=choices,
                ).execute()
                if selected and "[cancel]" not in selected:
                    uninstall_modules(selected)

            elif action == "list":
                list_modules()

            elif action == "status":
                show_status()

            elif action == "rice":
                # RICE submenu
                from InquirerPy import inquirer
                rice_choices = [
                    {"name": "[1] List RICEs", "value": "list"},
                    {"name": "[2] Set/Download RICE", "value": "set"},
                    {"name": "[3] Install from git URL", "value": "install"},
                    {"name": "[4] Delete local RICE", "value": "delete"},
                    {"name": "[5] Backup current", "value": "backup"},
                    {"name": "[x] Back", "value": "back"},
                ]
                rice_action = inquirer.select(
                    message="RICE manager:",
                    choices=rice_choices,
                ).execute()

                if rice_action == "list":
                    rice_list()
                elif rice_action == "set":
                    from _lib.utils.rice_manager import fetch_official_rices
                    official = fetch_official_rices()
                    rice_names = list(official.keys()) + ["[cancel]"]
                    selected = inquirer.select(
                        message="Select RICE to activate:",
                        choices=rice_names,
                    ).execute()
                    if selected and selected != "[cancel]":
                        rice_set(selected)
                elif rice_action == "install":
                    url = inquirer.text(message="Git URL:").execute()
                    if url:
                        rice_install(url)
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
                            rice_delete(selected)
                    else:
                        info_box("RICEs", "No local RICEs to delete")
                elif rice_action == "backup":
                    from _lib.utils.rice_manager import get_active_rice
                    active = get_active_rice()
                    if active:
                        rice_backup(active)
                    else:
                        info_box("RICEs", "No active RICE to backup")

            elif action == "update-core":
                update_core()

            elif action == "version":
                console.print(f"Shadow-SetUp v{__version__}")

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

def main():
    """Main entry point."""
    ensure_dirs()

    args = sys.argv[1:]

    # No args = interactive mode
    if not args:
        run_interactive()
        return

    command = args[0]
    module_args = args[1:] if len(args) > 1 else []

    # Commands that need full UI
    NEEDS_BANNER = {"list", "install", "update", "uninstall", "status", "update-core", "rice"}

    if command in NEEDS_BANNER:
        console.clear()

    try:
        if command in ("help", "--help", "-h"):
            show_help()
        elif command in ("version", "--version"):
            console.print(f"Shadow-SetUp v{__version__}")
        elif command == "list":
            list_modules()
        elif command == "install":
            if not module_args:
                error_box("Error", "Specify module(s) to install")
                sys.exit(1)
            install_modules(module_args)
        elif command == "update":
            if module_args and module_args[0] == "core":
                update_core()
            else:
                update_modules(module_args if module_args else None)
        elif command == "update-core":
            update_core()
        elif command == "uninstall":
            if not module_args:
                error_box("Error", "Specify module(s) to uninstall")
                sys.exit(1)
            uninstall_modules(module_args)
        elif command == "status":
            show_status(module_args if module_args else None)
        elif command == "rice":
            handle_rice(module_args)
        else:
            error_box("Error", f"Unknown command: {command}")
            show_help()
            sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[dim]Cancelled[/dim]")
        sys.exit(0)

if __name__ == "__main__":
    main()
