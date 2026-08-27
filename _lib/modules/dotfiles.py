"""Dotfiles module — Configuration files."""

import shutil
from pathlib import Path
from _lib.modules import BaseModule
from _lib.utils import backup_file, TERMUX_HOME
from _lib.utils.ui import console, success_box, error_box, info_box

class DotfilesModule(BaseModule):
    name = "dotfiles"
    description = "Configuration files (.zshrc, .p10k.zsh, .nanorc, .termux)"
    
    DOTFILES_DIR = Path(__file__).parent.parent.parent / "dotfiles"
    
    FILES = [
        ".zshrc",
        ".p10k.zsh",
        ".nanorc",
    ]
    
    TERMUX_FILES = [
        "colors.properties",
        "font.ttf",
        "termux.properties",
    ]
    
    def install(self) -> bool:
        try:
            info_box("Installing dotfiles", "Copying configuration files")
            
            for filename in self.FILES:
                src = self.DOTFILES_DIR / filename
                dst = Path.home() / filename
                
                if src.exists():
                    if dst.exists():
                        backup_file(dst)
                    shutil.copy2(src, dst)
                    success_box("File", f"{filename} copied")
                else:
                    console.print(f"  [warning]{filename} not found in repo[/warning]")
            
            termux_src = self.DOTFILES_DIR / ".termux"
            termux_dst = TERMUX_HOME
            termux_dst.mkdir(parents=True, exist_ok=True)
            
            for filename in self.TERMUX_FILES:
                src = termux_src / filename
                dst = termux_dst / filename
                
                if src.exists():
                    if dst.exists():
                        backup_file(dst)
                    shutil.copy2(src, dst)
                    success_box("File", f".termux/{filename} copied")
                else:
                    console.print(f"  [warning].termux/{filename} not found[/warning]")
            
            result = console.input("\n  [bold]Reload Termux settings? [Y/n]: [/bold]").strip()
            if result.lower() != "n":
                from _lib.utils import run_cmd
                run_cmd(["termux-reload-settings"])
                console.print("  [info]Settings reloaded[/info]")
            
            success_box("Dotfiles module", "Installation complete!")
            return True
            
        except Exception as e:
            error_box("Dotfiles module", f"Error: {str(e)}")
            return False
    
    def uninstall(self) -> bool:
        info_box("Dotfiles module", "Files won't be removed for safety")
        return True
    
    def update(self) -> bool:
        return self.install()
    
    def status(self) -> dict:
        installed = sum(1 for f in self.FILES if (Path.home() / f).exists())
        return {
            "status": "ok" if installed == len(self.FILES) else "partial",
            "details": f"{installed}/{len(self.FILES)} files installed"
        }
