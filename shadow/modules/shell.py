"""Shell module — zsh + Oh My Zsh + Powerlevel10k + plugins."""

import subprocess
from pathlib import Path
from shadow.modules import BaseModule
from shadow.utils import run_cmd, cmd_exists, backup_file, OH_MY_ZSH
from shadow.utils.ui import console, success_box, error_box, info_box, progress_bar

class ShellModule(BaseModule):
    name = "shell"
    description = "zsh + Oh My Zsh + Powerlevel10k + plugins"
    
    PLUGINS = [
        ("zsh-autosuggestions", "https://github.com/zsh-users/zsh-autosuggestions"),
        ("zsh-syntax-highlighting", "https://github.com/zsh-users/zsh-syntax-highlighting"),
    ]
    
    def install(self) -> bool:
        try:
            info_box("Installing shell module", "Setting up zsh environment")
            
            # Install zsh
            if not cmd_exists("zsh"):
                console.print("  [info]Installing zsh...[/info]")
                run_cmd(["pkg", "install", "-y", "zsh"], check=True)
                success_box("zsh", "Installed successfully")
            else:
                console.print("  [warning]zsh already installed, skipping...[/warning]")
            
            # Install Oh My Zsh
            if not OH_MY_ZSH.exists():
                console.print("  [info]Installing Oh My Zsh...[/info]")
                run_cmd([
                    "sh", "-c",
                    "RUNZSH=no CHSH=no sh -c \"$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)\""
                ], check=True)
                success_box("Oh My Zsh", "Installed successfully")
            else:
                console.print("  [warning]Oh My Zsh already installed, updating...[/warning]")
                run_cmd(["git", "-C", str(OH_MY_ZSH), "pull"], check=True)
            
            # Install Powerlevel10k
            p10k_dir = OH_MY_ZSH / "custom" / "themes" / "powerlevel10k"
            if not p10k_dir.exists():
                console.print("  [info]Installing Powerlevel10k...[/info]")
                run_cmd([
                    "git", "clone", "--depth=1",
                    "https://github.com/romkatv/powerlevel10k.git",
                    str(p10k_dir)
                ], check=True)
                success_box("Powerlevel10k", "Installed successfully")
            else:
                console.print("  [warning]Powerlevel10k already installed, updating...[/warning]")
                run_cmd(["git", "-C", str(p10k_dir), "pull"], check=True)
            
            # Install plugins
            plugins_dir = OH_MY_ZSH / "custom" / "plugins"
            plugins_dir.mkdir(parents=True, exist_ok=True)
            
            for name, repo in self.PLUGINS:
                plugin_dir = plugins_dir / name
                if not plugin_dir.exists():
                    console.print(f"  [info]Installing plugin: {name}...[/info]")
                    run_cmd([
                        "git", "clone", "--depth=1", repo, str(plugin_dir)
                    ], check=True)
                    success_box("Plugin", f"{name} installed")
                else:
                    console.print(f"  [warning]Plugin {name} already installed, updating...[/warning]")
                    run_cmd(["git", "-C", str(plugin_dir), "pull"], check=True)
            
            # Change shell to zsh
            current_shell = run_cmd(["sh", "-c", "echo $SHELL"], capture=True).stdout.strip()
            zsh_path = run_cmd(["which", "zsh"], capture=True).stdout.strip()
            if current_shell != zsh_path:
                console.print("  [info]Setting zsh as default shell...[/info]")
                run_cmd(["chsh", "-s", "zsh"])
            
            success_box("Shell module", "Installation complete!")
            return True
            
        except Exception as e:
            error_box("Shell module", f"Error: {str(e)}")
            return False
    
    def uninstall(self) -> bool:
        info_box("Shell module", "Use: chsh -s bash to switch back")
        return True
    
    def update(self) -> bool:
        try:
            info_box("Updating shell module", "Pulling latest changes...")
            
            if OH_MY_ZSH.exists():
                run_cmd(["git", "-C", str(OH_MY_ZSH), "pull"], check=True)
            
            p10k_dir = OH_MY_ZSH / "custom" / "themes" / "powerlevel10k"
            if p10k_dir.exists():
                run_cmd(["git", "-C", str(p10k_dir), "pull"], check=True)
            
            plugins_dir = OH_MY_ZSH / "custom" / "plugins"
            if plugins_dir.exists():
                for plugin_dir in plugins_dir.iterdir():
                    if (plugin_dir / ".git").exists():
                        run_cmd(["git", "-C", str(plugin_dir), "pull"], check=True)
            
            success_box("Shell module", "Update complete!")
            return True
            
        except Exception as e:
            error_box("Shell module", f"Error: {str(e)}")
            return False
    
    def status(self) -> dict:
        return {
            "status": "ok" if cmd_exists("zsh") else "missing",
            "details": f"zsh: {'installed' if cmd_exists('zsh') else 'missing'}"
        }
