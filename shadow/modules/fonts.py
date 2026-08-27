"""Fonts module — Nerd Fonts for Termux."""

import os
from pathlib import Path
from shadow.modules import BaseModule
from shadow.utils import run_cmd, backup_file
from shadow.utils.ui import console, success_box, error_box, info_box, warning_box

class FontsModule(BaseModule):
    name = "fonts"
    description = "Nerd Fonts for Termux"
    
    TERMUX_FONT_DIR = Path.home() / ".termux"
    FONT_FILE = "font.ttf"
    
    FONTS = {
        "jetbrains": "JetBrainsMono",
        "fira": "FiraCode",
        "hack": "Hack",
        "iosevka": "Iosevka",
        "meslo": "MesloLGS",
    }
    
    REPO_URL = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download"
    
    def install(self) -> bool:
        try:
            info_box("Installing fonts", "Select a Nerd Font")
            
            # Show available fonts
            console.print("\n  Available fonts:")
            for key, name in self.FONTS.items():
                console.print(f"    [cyan]•[/cyan] {key} ({name})")
            console.print()
            
            # Get user choice
            choice = console.input("  [bold]Which font? [jetbrains]: [/bold]").strip()
            choice = choice if choice in self.FONTS else "jetbrains"
            
            font_name = self.FONTS[choice]
            font_url = f"{self.REPO_URL}/{font_name}NerdFont-Regular.ttf"
            
            # Backup existing font
            font_path = self.TERMUX_FONT_DIR / self.FONT_FILE
            if font_path.exists():
                backup_file(font_path)
                console.print("  [warning]Existing font backed up[/warning]")
            
            # Download font
            console.print(f"  [info]Downloading {font_name} Nerd Font...[/info]")
            self.TERMUX_FONT_DIR.mkdir(parents=True, exist_ok=True)
            
            result = run_cmd([
                "curl", "-fsSL", font_url, "-o", str(font_path)
            ])
            
            if result.returncode == 0:
                success_box("Font", f"{font_name} downloaded successfully")
                
                # Reload Termux settings
                if run_cmd(["command", "-v", "termux-reload-settings"]).returncode == 0:
                    run_cmd(["termux-reload-settings"])
                    console.print("  [info]Termux settings reloaded[/info]")
                
                return True
            else:
                # Fallback to repo font
                warning_box("Font", "Download failed, using repo font...")
                repo_font = self.shadow_home / "dotfiles" / ".termux" / self.FONT_FILE
                if repo_font.exists():
                    import shutil
                    shutil.copy2(repo_font, font_path)
                    success_box("Font", "Repo font installed")
                    return True
                else:
                    error_box("Font", "No font available")
                    return False
                    
        except Exception as e:
            error_box("Fonts module", f"Error: {str(e)}")
            return False
    
    def uninstall(self) -> bool:
        info_box("Fonts module", "Font won't be removed for safety")
        return True
    
    def update(self) -> bool:
        return self.install()
    
    def status(self) -> dict:
        font_path = self.TERMUX_FONT_DIR / self.FONT_FILE
        if font_path.exists():
            return {"status": "ok", "details": "Font installed"}
        return {"status": "missing", "details": "No font installed"}
