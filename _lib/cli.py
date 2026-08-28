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
from _lib.commands import get_command, get_all_commands

# Import modules
from _lib.modules.shell import ShellModule
from _lib.modules.tools import ToolsModule
from _lib.modules.fonts import FontsModule
from _lib.modules.dotfiles import DotfilesModule
from _lib.modules.aliases import AliasesModule

MODULES = {
    "shell": ShellModule(),
    "tools": ToolsModule(),
    "fonts": FontsModule(),
    "dotfiles": DotfilesModule(),
    "aliases": AliasesModule(),
}

# Metadata for each module (dynamic help)
MODULE_META = {
    "shell": {"package": "zsh, git", "config": "~/.oh-my-zsh, ~/.p10k.zsh"},
    "tools": {"package": "pkg", "config": ""},
    "fonts": {"package": "curl", "config": "~/.termux/font.ttf"},
    "dotfiles": {"package": "", "config": "~/.zshrc, ~/.nanorc, ~/.termux/*"},
    "aliases": {"package": "", "config": "~/.zshrc (source aliases.sh)"},
}

def show_help():
    """Display help information."""
    banner()
    console.print("[bold]Usage:[/bold] sw [command]")
    console.print()
    console.print("[bold]Commands:[/bold]")
    for cmd in get_all_commands():
        console.print(f"  [cyan]{cmd.name:<14}[/cyan] {cmd.description}")
    console.print()
    console.print("[bold]Modules:[/bold]")
    for name, mod in MODULES.items():
        meta = MODULE_META.get(name, {})
        pkg = meta.get("package", "")
        pkg_info = f" [dim]({pkg})[/dim]" if pkg else ""
        console.print(f"  [cyan]•[/cyan] {name} — {mod.description}{pkg_info}")
    console.print()
    console.print("[bold]Examples:[/bold]")
    console.print("  sw                     # Interactive menu")
    console.print("  sw install shell       # Install zsh + plugins")
    console.print("  sw update              # Update all modules")
    console.print("  sw status              # Show all status")
    console.print()
    console.print("[dim]Shadow-TermDev · https://Shadow-TermDev.github.io[/dim]")

def list_modules():
    """List all available modules."""
    banner()
    modules_info = {}
    for name, mod in MODULES.items():
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
        for name, mod in MODULES.items():
            status = mod.status()
            status_data[name] = {
                "status": "ok" if status.get("status") == "ok" else "missing",
                "details": status.get("details", "")
            }
        status_table(status_data)

def update_core():
    """Update Shadow-SetUp from GitHub with clean progress."""
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
                choices = list(MODULES.keys()) + ["[cancel]"]
                selected = inquirer.checkbox(
                    message="Select modules to install:",
                    choices=choices,
                ).execute()
                if selected and "[cancel]" not in selected:
                    install_modules(selected)
            
            elif action == "update":
                choices = list(MODULES.keys()) + ["all", "[cancel]"]
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
                choices = list(MODULES.keys()) + ["[cancel]"]
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
    NEEDS_BANNER = {"list", "install", "update", "uninstall", "status", "update-core"}
    
    if command in NEEDS_BANNER:
        console.clear()
    
    try:
        if command == "help" or command == "--help" or command == "-h":
            show_help()
        elif command == "version" or command == "--version":
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
        else:
            error_box("Error", f"Unknown command: {command}")
            show_help()
            sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[dim]Cancelled[/dim]")
        sys.exit(0)

if __name__ == "__main__":
    main()
