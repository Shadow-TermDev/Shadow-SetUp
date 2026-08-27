"""Fonts module — Nerd Fonts for Termux."""

import shutil
from pathlib import Path
from _lib.modules import BaseModule
from _lib.utils import run_cmd, backup_file, TERMUX_HOME
from _lib.utils.ui import console, success_box, error_box, info_box, warning_box

class FontsModule(BaseModule):
    name = "fonts"
    description = "Nerd Fonts for Termux"
    
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
        """Install font — asks user for selection."""
        try:
            info_box("Installing fonts", "Select a Nerd Font")
            
            console.print("\n  Available fonts:")
            for key, name in self.FONTS.items():
                console.print(f"    [cyan]•[/cyan] {key} ({name})")
            console.print(f"    [cyan]•[/cyan] [bold]keep[/bold] — Keep current font")
            console.print()
            
            choice = console.input("  [bold]Which font? [jetbrains]: [/bold]").strip()
            
            if choice.lower() == "keep":
                font_path = TERMUX_HOME / self.FONT_FILE
                if font_path.exists():
                    info_box("Font", "Keeping current font")
                    return True
                else:
                    warning_box("Font", "No font installed yet, select one below")
                    choice = ""
            
            choice = choice if choice in self.FONTS else "jetbrains"
            return self._install_font(choice)
                    
        except Exception as e:
            error_box("Fonts module", f"Error: {str(e)}")
            return False
    
    def _install_font(self, choice: str) -> bool:
        """Download and install a font by choice key."""
        font_name = self.FONTS.get(choice, "JetBrainsMono")
        font_url = f"{self.REPO_URL}/{font_name}NerdFont-Regular.ttf"
        font_path = TERMUX_HOME / self.FONT_FILE
        
        # Backup existing
        if font_path.exists():
            backup_file(font_path)
            console.print("  [warning]Existing font backed up[/warning]")
        
        console.print(f"  [info]Downloading {font_name}...[/info]")
        TERMUX_HOME.mkdir(parents=True, exist_ok=True)
        
        result = run_cmd(["curl", "-fsSL", font_url, "-o", str(font_path)])
        
        if result.returncode == 0:
            success_box("Font", f"{font_name} installed")
            self._reload_settings()
            return True
        else:
            # Fallback to repo font
            warning_box("Font", "Download failed, using repo font...")
            repo_font = Path(__file__).parent.parent.parent / "dotfiles" / ".termux" / self.FONT_FILE
            if repo_font.exists():
                shutil.copy2(repo_font, font_path)
                success_box("Font", "Repo font installed")
                self._reload_settings()
                return True
            else:
                error_box("Font", "No font available")
                return False
    
    def _reload_settings(self):
        """Reload Termux settings."""
        if run_cmd(["command", "-v", "termux-reload-settings"]).returncode == 0:
            run_cmd(["termux-reload-settings"])
            console.print("  [info]Termux settings reloaded[/info]")
    
    def uninstall(self) -> bool:
        info_box("Fonts module", "Font won't be removed for safety")
        return True
    
    def update(self) -> bool:
        """Update — just check status, don't ask for font selection."""
        font_path = TERMUX_HOME / self.FONT_FILE
        if font_path.exists():
            info_box("Fonts module", "Font already installed, skipping")
            return True
        else:
            warning_box("Fonts module", "No font installed. Run: sw install fonts")
            return False
    
    def status(self) -> dict:
        font_path = TERMUX_HOME / self.FONT_FILE
        if font_path.exists():
            return {"status": "ok", "details": "Font installed"}
        return {"status": "missing", "details": "No font installed"}
