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
        """Install default font (JetBrains Mono)."""
        try:
            font_path = TERMUX_HOME / self.FONT_FILE
            
            if font_path.exists():
                info_box("Font", "Font already installed, skipping")
                return True
            
            # Install default font
            return self._install_font("jetbrains")
                    
        except Exception as e:
            error_box("Fonts module", f"Error: {str(e)}")
            return False
    
    def _install_font(self, choice: str) -> bool:
        """Download and install a font by choice key."""
        font_name = self.FONTS.get(choice, "JetBrainsMono")
        font_url = f"{self.REPO_URL}/{font_name}NerdFont-Regular.ttf"
        font_path = TERMUX_HOME / self.FONT_FILE
        
        TERMUX_HOME.mkdir(parents=True, exist_ok=True)
        
        console.print(f"  [info]Downloading {font_name}...[/info]")
        
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
        """Update — just check status."""
        font_path = TERMUX_HOME / self.FONT_FILE
        if font_path.exists():
            info_box("Fonts module", "Font already installed")
            return True
        else:
            warning_box("Fonts module", "No font installed. Run: sw install fonts")
            return False
    
    def status(self) -> dict:
        font_path = TERMUX_HOME / self.FONT_FILE
        if font_path.exists():
            return {"status": "ok", "details": "Font installed"}
        return {"status": "missing", "details": "No font installed"}
