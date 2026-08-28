"""Dotfiles module — Configuration files."""

import shutil
from pathlib import Path
from _lib.modules import BaseModule
from _lib.utils import backup_file, TERMUX_HOME, SHADOW_DATA
from _lib.utils.ui import console, success_box, error_box, info_box

class DotfilesModule(BaseModule):
    name = "dotfiles"
    description = "Configuration files (.zshrc, .p10k.zsh, aliases)"
    
    def install(self) -> bool:
        try:
            info_box("Installing dotfiles", "Setting up configuration")
            
            dotfiles_dir = SHADOW_DATA / "dotfiles"
            
            # Copy .zshrc
            src_zshrc = dotfiles_dir / ".zshrc"
            dst_zshrc = Path.home() / ".zshrc"
            if src_zshrc.exists():
                if dst_zshrc.exists():
                    backup_file(dst_zshrc)
                shutil.copy2(src_zshrc, dst_zshrc)
                success_box("File", ".zshrc installed")
            
            # Copy aliases
            src_aliases = dotfiles_dir / "aliases.sh"
            dst_aliases = dotfiles_dir / "aliases.sh"
            if src_aliases.exists():
                success_box("File", "aliases.sh ready")
            
            # Termux config — only if not already set by RICE
            termux_dst = TERMUX_HOME
            termux_dst.mkdir(parents=True, exist_ok=True)
            
            for filename in ["colors.properties", "font.ttf", "termux.properties"]:
                src = dotfiles_dir / ".termux" / filename
                dst = termux_dst / filename
                if src.exists() and not dst.exists():
                    shutil.copy2(src, dst)
            
            # Reload Termux settings
            try:
                result = console.input("\n  [bold]Reload Termux settings? [Y/n]: [/bold]").strip()
                if result.lower() != "n":
                    from _lib.utils import run_cmd
                    run_cmd(["termux-reload-settings"])
                    console.print("  [info]Settings reloaded[/info]")
            except (EOFError, KeyboardInterrupt):
                pass
            
            success_box("Dotfiles module", "Configuration ready!")
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
        has_zshrc = (Path.home() / ".zshrc").exists()
        return {
            "status": "ok" if has_zshrc else "missing",
            "details": ".zshrc installed" if has_zshrc else ".zshrc missing"
        }
