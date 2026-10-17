"""Dotfiles module — Configuration files."""

import shutil
from pathlib import Path
from _lib.modules import BaseModule
from _lib.utils import backup_file, TERMUX_HOME, SHADOW_DATA
from _lib.utils.ui import console, success_box, error_box, info_box, warning_box

# Marker used to tell the framework .zshrc apart from a foreign one (OMZ/p10k)
ZSHRC_MARKERS = ("Shadow-SetUp", "active_rice.sh")


class DotfilesModule(BaseModule):
    name = "dotfiles"
    description = "Configuration files (.zshrc, .p10k.zsh, aliases)"

    def _dotfiles_dir(self) -> Path:
        """Best source for framework dotfiles (installed data or dev checkout)."""
        candidates = [
            SHADOW_DATA / "dotfiles",
            Path(__file__).resolve().parents[2] / "dotfiles",
        ]
        for candidate in candidates:
            if (candidate / ".zshrc").exists():
                return candidate
        return SHADOW_DATA / "dotfiles"

    def _is_framework_zshrc(self, path: Path) -> bool:
        """True when the rc file is the Shadow-SetUp one (or wires the RICE up)."""
        try:
            if not path.exists():
                return False
            content = path.read_text()
        except Exception:
            return False
        return any(marker in content for marker in ZSHRC_MARKERS)

    def install(self) -> bool:
        try:
            info_box("Installing dotfiles", "Setting up configuration")

            dotfiles_dir = self._dotfiles_dir()
            installed_dir = SHADOW_DATA / "dotfiles"
            installed_dir.mkdir(parents=True, exist_ok=True)

            # Restore framework files that a partial install may have missed
            for required in (".zshrc", ".nanorc", "aliases.sh"):
                src = dotfiles_dir / required
                dst = installed_dir / required
                if src.exists() and not dst.exists():
                    shutil.copy2(src, dst)

            # Copy .zshrc — always (with backup), never trust a foreign rc file
            src_zshrc = installed_dir / ".zshrc"
            dst_zshrc = Path.home() / ".zshrc"
            if src_zshrc.exists():
                if dst_zshrc.exists() and not self._is_framework_zshrc(dst_zshrc):
                    backup_file(dst_zshrc)
                shutil.copy2(src_zshrc, dst_zshrc)
                success_box("File", ".zshrc installed")
            else:
                # No framework rc available: at least wire the active RICE up
                from _lib.utils.rice_manager import ensure_zshrc_sources_rice
                if ensure_zshrc_sources_rice():
                    success_box("File", "active_rice.sh sourcing added to .zshrc")
                else:
                    warning_box("Dotfiles", ".zshrc source not found — skipped")

            # Base aliases (rice-level aliases live in ~/.shadow-setup/aliases.sh
            # and are owned by the active RICE, so they are left untouched here)
            src_aliases = installed_dir / "aliases.sh"
            if src_aliases.exists():
                success_box("File", "aliases.sh ready")

            # Termux base config — a RICE always wins over the base files
            from _lib.utils.rice_manager import get_active_rice, remove_motd
            termux_dst = TERMUX_HOME
            termux_dst.mkdir(parents=True, exist_ok=True)

            if get_active_rice():
                console.print("  [dim]Active RICE owns ~/.termux — keeping its colors/font[/dim]")
            else:
                for filename in ["colors.properties", "font.ttf", "termux.properties"]:
                    src = dotfiles_dir / ".termux" / filename
                    dst = termux_dst / filename
                    if src.exists():
                        shutil.copy2(src, dst)

            # Termux MOTD would print its own banner over the RICE greeting
            if remove_motd():
                console.print("  [dim]Termux MOTD removed[/dim]")

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
        zshrc = Path.home() / ".zshrc"
        if not zshrc.exists():
            return {"status": "missing", "details": ".zshrc missing"}
        if self._is_framework_zshrc(zshrc):
            return {"status": "ok", "details": ".zshrc installed (Shadow-SetUp)"}
        return {
            "status": "missing",
            "details": ".zshrc present but not the Shadow-SetUp one",
        }
