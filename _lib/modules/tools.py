"""Tools module — Essential packages for Termux."""

import subprocess
from _lib.modules import BaseModule
from _lib.utils import run_cmd, pkg_installed
from _lib.utils.ui import console, success_box, error_box, info_box

class ToolsModule(BaseModule):
    name = "tools"
    description = "Essential packages (git, curl, bat, eza, fzf, etc.)"
    
    PACKAGES = [
        "git", "curl", "wget", "nano",
        "bat", "eza", "fd", "fzf", "zoxide",
        "python", "python-pip", "nodejs-lts",
        "termux-api", "openssh", "man",
    ]
    
    def install(self) -> bool:
        try:
            info_box("Installing tools", f"{len(self.PACKAGES)} packages")
            
            installed = 0
            skipped = 0
            
            for pkg in self.PACKAGES:
                if pkg_installed(pkg):
                    console.print(f"  [warning]{pkg} already installed, skipping...[/warning]")
                    skipped += 1
                else:
                    console.print(f"  [info]Installing {pkg}...[/info]")
                    result = run_cmd(["pkg", "install", "-y", pkg])
                    if result.returncode == 0:
                        success_box("Package", f"{pkg} installed")
                        installed += 1
                    else:
                        console.print(f"  [warning]Failed to install {pkg}[/warning]")
            
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
        missing = [p for p in self.PACKAGES if not pkg_installed(p)]
        return {
            "status": "ok" if not missing else "partial",
            "details": f"{len(self.PACKAGES) - len(missing)}/{len(self.PACKAGES)} installed"
        }
