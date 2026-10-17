"""Aliases module — Shell aliases and functions."""

from pathlib import Path
from _lib.modules import BaseModule
from _lib.utils.ui import console, success_box, error_box, info_box

class AliasesModule(BaseModule):
    name = "aliases"
    description = "Shell aliases and functions"
    
    ALIASES_FILE = Path.home() / ".shadow-setup" / "dotfiles" / "aliases.sh"
    ZSHRC = Path.home() / ".zshrc"
    BLOCK_START = "# >>> Shadow-SetUp aliases >>>"
    BLOCK_END = "# <<< Shadow-SetUp aliases <<<"
    # How the framework .zshrc references the same file (with $HOME unexpanded)
    WIRED_MARKERS = (
        str(ALIASES_FILE),
        "$HOME/.shadow-setup/dotfiles/aliases.sh",
        "dotfiles/aliases.sh",
    )

    def _content(self) -> str:
        try:
            return self.ZSHRC.read_text() if self.ZSHRC.exists() else ""
        except Exception:
            return ""

    def _is_wired(self, content: str) -> bool:
        """True when .zshrc already sources the base aliases file."""
        return "aliases.sh" in content and any(m in content for m in self.WIRED_MARKERS)

    def _strip_blocks(self, content: str) -> str:
        """Drop our previous blocks (marker-based and legacy plain lines)."""
        out = []
        skipping = False
        for line in content.splitlines():
            if line.startswith(self.BLOCK_START):
                skipping = True
                continue
            if line.startswith(self.BLOCK_END):
                skipping = False
                continue
            if skipping:
                continue
            stripped = line.strip()
            if stripped == "# Shadow-SetUp Aliases":
                continue
            if stripped.startswith("source ") and "aliases.sh" in stripped and "shadow-setup" in stripped:
                continue
            out.append(line)
        return "\n".join(out)

    def install(self) -> bool:
        try:
            info_box("Installing aliases", "Setting up aliases module")
            
            if not self.ALIASES_FILE.exists():
                error_box("Aliases", "aliases.sh not found in repo")
                return False

            content = self._content()
            if self._is_wired(content):
                console.print("  [dim]Aliases already sourced by .zshrc[/dim]")
                success_box("Aliases module", "Aliases ready")
                return True

            # Remove any stale block, then append a single marker-guarded one
            content = self._strip_blocks(content).rstrip()
            block = (
                f"\n{self.BLOCK_START}\n"
                f"source {self.ALIASES_FILE}\n"
                f"{self.BLOCK_END}\n"
            )
            if content:
                content += "\n"
            self.ZSHRC.parent.mkdir(parents=True, exist_ok=True)
            self.ZSHRC.write_text(content + block)

            success_box("Aliases module", "Aliases added to .zshrc")
            return True
            
        except Exception as e:
            error_box("Aliases module", f"Error: {str(e)}")
            return False
    
    def uninstall(self) -> bool:
        try:
            if self.ZSHRC.exists():
                content = self._strip_blocks(self._content())
                self.ZSHRC.write_text(content.rstrip() + "\n")
                success_box("Aliases module", "Aliases removed from .zshrc")
            return True
        except Exception as e:
            error_box("Aliases module", f"Error: {str(e)}")
            return False
    
    def update(self) -> bool:
        return self.install()
    
    def status(self) -> dict:
        if not self.ALIASES_FILE.exists():
            return {"status": "missing", "details": "aliases.sh not found"}
        if self._is_wired(self._content()):
            return {"status": "ok", "details": f"{self.ALIASES_FILE}"}
        return {
            "status": "missing",
            "details": "aliases.sh present but not sourced by .zshrc",
        }
