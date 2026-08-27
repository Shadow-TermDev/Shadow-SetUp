#!/usr/bin/env python3
"""
Shadow-SetUp CLI — Modular Termux Environment Manager.

Usage:
    shadow <command> [module...]
    
Commands:
    install <module>   Install a module
    update [module]    Update module(s)
    uninstall <module> Uninstall a module
    list               List available modules
    status [module]    Show module status
    update-core        Update Shadow-SetUp from GitHub
    version            Show version
    help               Show this help
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shadow import __version__
from shadow.utils.ui import (
    console, banner, success_box, error_box, 
    info_box, module_table, status_table
)
from shadow.utils import SHADOW_HOME, ensure_dirs

# Import modules
from shadow.modules.shell import ShellModule
from shadow.modules.tools import ToolsModule
from shadow.modules.fonts import FontsModule
from shadow.modules.dotfiles import DotfilesModule
from shadow.modules.aliases import AliasesModule

MODULES = {
    "shell": ShellModule(),
    "tools": ToolsModule(),
    "fonts": FontsModule(),
    "dotfiles": DotfilesModule(),
    "aliases": AliasesModule(),
}

def show_help():
    """Display help information."""
    banner()
    console.print("[bold]Usage:[/bold] shadow <command> [module]")
    console.print()
    console.print("[bold]Commands:[/bold]")
    console.print("  install <module>   Install a module")
    console.print("  update [module]    Update module(s)")
    console.print("  uninstall <module> Uninstall a module")
    console.print("  list               List available modules")
    console.print("  status [module]    Show module status")
    console.print("  update-core        Update Shadow-SetUp from GitHub")
    console.print("  version            Show version")
    console.print("  help               Show this help")
    console.print()
    console.print("[bold]Modules:[/bold]")
    for name, mod in MODULES.items():
        console.print(f"  [cyan]•[/cyan] {name} — {mod.description}")
    console.print()
    console.print("[bold]Examples:[/bold]")
    console.print("  shadow install shell    # Install zsh + plugins")
    console.print("  shadow update           # Update all modules")
    console.print("  shadow update shell     # Update only shell")
    console.print("  shadow status           # Show all status")

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
    """Update Shadow-SetUp from GitHub."""
    import subprocess
    import shutil
    
    banner()
    info_box("Updating Shadow-SetUp", "Cloning latest version from GitHub...")
    
    cache_dir = Path.home() / ".cache" / "shadow-setup"
    temp_dir = cache_dir / "shadow-update"
    
    try:
        # Clean temp dir
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        # Clone repo
        result = subprocess.run([
            "git", "clone", "--depth=1",
            "https://github.com/Shadow-TermDev/Shadow-SetUp.git",
            str(temp_dir)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            error_box("Update failed", "Could not clone repository")
            return
        
        # Copy files
        shadow_pkg = temp_dir / "shadow"
        if shadow_pkg.exists():
            shutil.rmtree(SHADOW_HOME / "shadow")
            shutil.copytree(shadow_pkg, SHADOW_HOME / "shadow")
        
        # Copy other files
        for f in ["setup.sh", "README.md"]:
            src = temp_dir / f
            if src.exists():
                shutil.copy2(src, SHADOW_HOME / f)
        
        # Copy dotfiles
        dotfiles_src = temp_dir / "dotfiles"
        if dotfiles_src.exists():
            shutil.copytree(dotfiles_src, SHADOW_HOME / "dotfiles", dirs_exist_ok=True)
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        success_box("Update complete!", "Shadow-SetUp has been updated to the latest version")
        
    except Exception as e:
        error_box("Update failed", str(e))

def main():
    """Main entry point."""
    ensure_dirs()
    
    # Clear screen for clean CLI experience
    console.clear()
    
    args = sys.argv[1:]
    
    if not args:
        show_help()
        return
    
    command = args[0]
    module_args = args[1:] if len(args) > 1 else []
    
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

if __name__ == "__main__":
    main()
