"""Tools module — Essential packages for Termux."""

import subprocess
from _lib.modules import BaseModule
from _lib.utils import run_cmd, pkg_installed, pkg_installed_many
from _lib.utils.ui import console, success_box, error_box, info_box, warning_box

# Heavy packages (nodejs-lts) on a slow mobile link can take minutes: give
# pkg enough room so the UI never sits on a silent 120s timeout.
PKG_TIMEOUT = 300


class ToolsModule(BaseModule):
    name = "tools"
    description = "Essential packages (git, curl, bat, eza, fzf, etc.)"

    # Everything the framework/RICEs assume is present
    CRITICAL_PACKAGES = [
        "git", "curl", "wget", "nano",
        "python", "python-pip",
    ]

    # Nice to have — a failure here only downgrades the module to a warning
    OPTIONAL_PACKAGES = [
        "bat", "eza", "fd", "fzf", "zoxide",
        "nodejs-lts", "termux-api", "openssh", "man",
    ]

    @property
    def PACKAGES(self) -> list[str]:
        return self.CRITICAL_PACKAGES + self.OPTIONAL_PACKAGES

    def _install_one(self, pkg: str) -> bool:
        """Install a single package. Never raises."""
        console.print(f"  [info]Installing {pkg}...[/info]")
        try:
            result = run_cmd(["pkg", "install", "-y", pkg], timeout=PKG_TIMEOUT)
        except subprocess.TimeoutExpired:
            console.print(
                f"  [warning]{pkg} timed out after {PKG_TIMEOUT}s — "
                f"retry later with: pkg install -y {pkg}[/warning]"
            )
            return False
        if result.returncode == 0:
            success_box("Package", f"{pkg} installed")
            return True
        return False

    def install(self) -> bool:
        try:
            info_box("Installing tools", f"{len(self.PACKAGES)} packages")

            installed = 0
            skipped = 0
            failed_critical: list[str] = []
            failed_optional: list[str] = []

            # Critical first: a slow optional package must never block them
            for pkg in self.CRITICAL_PACKAGES:
                if pkg_installed(pkg):
                    console.print(f"  [dim]{pkg} already installed, skipping...[/dim]")
                    skipped += 1
                elif self._install_one(pkg):
                    installed += 1
                else:
                    failed_critical.append(pkg)

            for pkg in self.OPTIONAL_PACKAGES:
                if pkg_installed(pkg):
                    console.print(f"  [dim]{pkg} already installed, skipping...[/dim]")
                    skipped += 1
                elif self._install_one(pkg):
                    installed += 1
                else:
                    failed_optional.append(pkg)
                    console.print(
                        f"  [dim]Optional package {pkg} failed — "
                        f"retry with: pkg install -y {pkg}[/dim]"
                    )

            if failed_critical:
                error_box(
                    "Tools module",
                    f"Critical packages failed: {', '.join(failed_critical)}\n"
                    "  Retry with: sw install tools",
                )
                return False

            if failed_optional:
                warning_box(
                    "Tools module",
                    f"Installed: {installed}, Skipped: {skipped} — "
                    f"optional missing: {', '.join(failed_optional)}",
                )
            else:
                success_box("Tools module", f"Installed: {installed}, Skipped: {skipped}")
            return True

        except Exception as e:
            error_box("Tools module", f"Error: {str(e)}")
            return False
    
    def uninstall(self) -> bool:
        info_box("Tools module", "Packages won't be removed for safety")
        return True
    
    def update(self) -> bool:
        try:
            from _lib.utils import run_cmd
            info_box("Updating tools", "Running pkg update...")
            run_cmd(["pkg", "update", "-y"], capture=True, timeout=300)
            run_cmd(["pkg", "upgrade", "-y"], capture=True, timeout=300)
            success_box("Tools module", "Update complete!")
            return True
        except KeyboardInterrupt:
            info_box("Tools module", "Update cancelled")
            return False
        except subprocess.TimeoutExpired:
            error_box("Tools module", "Update timed out")
            return False
        except Exception as e:
            error_box("Tools module", f"Error: {str(e)}")
            return False
    
    def status(self) -> dict:
        results = pkg_installed_many(self.PACKAGES)
        missing = [p for p, ok in results.items() if not ok]
        return {
            "status": "ok" if not missing else "partial",
            "details": f"{len(self.PACKAGES) - len(missing)}/{len(self.PACKAGES)} installed"
        }
