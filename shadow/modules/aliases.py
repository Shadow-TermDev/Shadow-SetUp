"""Aliases module — Shell aliases and functions."""

import shutil
from pathlib import Path
from shadow.modules import BaseModule
from shadow.utils import backup_file
from shadow.utils.ui import console, success_box, error_box, info_box

class AliasesModule(BaseModule):
    name = "aliases"
    description = "Shell aliases and functions"
    
    ALIASES_FILE = Path.home() / "Shadow-SetUp" / "dotfiles" / "aliases.sh"
    ZSHRC = Path.home() / ".zshrc"
    
    def install(self) -> bool:
        try:
            info_box("Installing aliases", "Setting up aliases module")
            
            if not self.ALIASES_FILE.exists():
                error_box("Aliases", "aliases.sh not found in repo")
                return False
            
            # Check if already in .zshrc
            if self.ZSHRC.exists():
                content = self.ZSHRC.read_text()
                if "source.*aliases.sh" in content or "shadow-aliases" in content:
                    console.print("  [warning]Aliases already in .zshrc, updating...[/warning]")
                    # Remove old entries
                    lines = [l for l in content.splitlines() 
                            if "shadow-aliases" not in l and "source.*aliases.sh" not in l]
                    self.ZSHRC.write_text("\n".join(lines))
            
            # Add source line to .zshrc
            source_line = f"\n# Shadow-SetUp Aliases\nsource {self.ALIASES_FILE}\n"
            
            with open(self.ZSHRC, "a") as f:
                f.write(source_line)
            
            success_box("Aliases module", "Aliases added to .zshrc")
            return True
            
        except Exception as e:
            error_box("Aliases module", f"Error: {str(e)}")
            return False
    
    def uninstall(self) -> bool:
        try:
            if self.ZSHRC.exists():
                content = self.ZSHRC.read_text()
                lines = [l for l in content.splitlines() 
                        if "shadow-aliases" not in l and "source.*aliases.sh" not in l]
                self.ZSHRC.write_text("\n".join(lines))
                success_box("Aliases module", "Aliases removed from .zshrc")
            return True
        except Exception as e:
            error_box("Aliases module", f"Error: {str(e)}")
            return False
    
    def update(self) -> bool:
        return self.install()
    
    def status(self) -> dict:
        if self.ALIASES_FILE.exists():
            return {"status": "ok", "details": f"{self.ALIASES_FILE}"}
        return {"status": "missing", "details": "aliases.sh not found"}
