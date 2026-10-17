"""Shell module — zsh + Oh My Zsh + Powerlevel10k + plugins.

Designed so a slow mobile network cannot kill the whole module:
  zsh -> Oh My Zsh -> Powerlevel10k -> plugins -> chsh
Each step is independent. Only a missing zsh is fatal; everything else
degrades to a warning and `sw install shell` can be re-run to repair it.
"""

import shutil
import subprocess
from pathlib import Path
from _lib.modules import BaseModule
from _lib.utils import run_cmd, cmd_exists, OH_MY_ZSH
from _lib.utils.ui import console, success_box, error_box, info_box, warning_box

# Slow mobile networks routinely exceed the 120s default — a single timeout
# used to abort the module and left the user stuck on bash.
NET_TIMEOUT = 300
NET_RETRIES = 3
PULL_TIMEOUT = 120

OMZ_REPO = "https://github.com/ohmyzsh/ohmyzsh.git"
OMZ_INSTALL_URL = "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
P10K_REPO = "https://github.com/romkatv/powerlevel10k.git"
P10K_THEME_FILE = "powerlevel10k.zsh-theme"


class ShellModule(BaseModule):
    name = "shell"
    description = "zsh + Oh My Zsh + Powerlevel10k + plugins"

    PLUGINS = [
        ("zsh-autosuggestions", "https://github.com/zsh-users/zsh-autosuggestions"),
        ("zsh-syntax-highlighting", "https://github.com/zsh-users/zsh-syntax-highlighting"),
    ]

    OPTIONAL_PLUGINS = [
        ("fzf", "https://github.com/junegunn/fzf"),
    ]

    @property
    def p10k_dir(self) -> Path:
        """Powerlevel10k theme dir (referenced by the framework .zshrc)."""
        return OH_MY_ZSH / "custom" / "themes" / "powerlevel10k"

    # -----------------------------------------------------------
    # Low level helpers
    # -----------------------------------------------------------
    def _run_git(self, args: list[str], label: str, attempts: int = 1,
                 timeout: int = NET_TIMEOUT) -> bool:
        """Run a git command with retries. Never raises: a timeout on a slow
        network is an expected condition, not a module-killing error."""
        for attempt in range(1, attempts + 1):
            shown = f"{label} (attempt {attempt}/{attempts})" if attempts > 1 else label
            console.print(f"  [info]{shown}...[/info]")
            try:
                result = run_cmd(args, timeout=timeout)
            except subprocess.TimeoutExpired:
                console.print(f"  [warning]{label} timed out after {timeout}s[/warning]")
                continue
            except FileNotFoundError as e:
                console.print(f"  [warning]{label} failed: {e}[/warning]")
                return False
            if result.returncode == 0:
                return True
            detail = (result.stderr or result.stdout or "").strip().splitlines()
            console.print(
                f"  [warning]{label} failed{': ' + detail[0] if detail else ''}[/warning]"
            )
        return False

    def _run_pkg(self, pkg: str) -> bool:
        """Install a Termux package with a generous timeout + one retry."""
        for attempt in (1, 2):
            console.print(f"  [info]Installing {pkg} (attempt {attempt}/2)...[/info]")
            try:
                result = run_cmd(["pkg", "install", "-y", pkg], timeout=NET_TIMEOUT)
            except subprocess.TimeoutExpired:
                console.print(f"  [warning]{pkg} timed out after {NET_TIMEOUT}s[/warning]")
                continue
            if result.returncode == 0:
                return True
        return False

    # -----------------------------------------------------------
    # Steps
    # -----------------------------------------------------------
    def _install_zsh(self) -> bool:
        """Step 1 — zsh. The only fatal step: nothing else works without it."""
        if cmd_exists("zsh"):
            console.print("  [dim]zsh already installed[/dim]")
            return True
        if self._run_pkg("zsh") and cmd_exists("zsh"):
            success_box("zsh", "Installed successfully")
            return True
        error_box("zsh", "Install failed — retry with: sw install shell\n  Or manually: pkg install -y zsh")
        return False

    def _salvage_broken_omz(self) -> Path | None:
        """Move a half-cloned ~/.oh-my-zsh aside.

        git refuses to clone into a non-empty dir, so an interrupted install
        must be cleared first. Returns the backup dir (custom/ is restored
        from it later) or None when there is nothing worth keeping.
        """
        if not OH_MY_ZSH.exists() or (OH_MY_ZSH / "oh-my-zsh.sh").exists():
            return None
        backup = OH_MY_ZSH.with_name(".oh-my-zsh.broken")
        try:
            shutil.rmtree(backup, ignore_errors=True)
            OH_MY_ZSH.rename(backup)
            console.print(f"  [warning]Broken Oh My Zsh moved to {backup}[/warning]")
            return backup
        except OSError as e:
            console.print(f"  [warning]Could not clear broken Oh My Zsh: {e}[/warning]")
            shutil.rmtree(OH_MY_ZSH, ignore_errors=True)
            return None

    def _restore_omz_backup(self, backup: Path | None) -> None:
        """Merge a salvaged ~/.oh-my-zsh back (its custom/ survives a re-clone)."""
        if backup is None or not backup.exists():
            return
        try:
            custom = backup / "custom"
            if custom.exists():
                target = OH_MY_ZSH / "custom"
                target.mkdir(parents=True, exist_ok=True)
                for item in custom.iterdir():
                    if not (target / item.name).exists():
                        shutil.move(str(item), str(target / item.name))
            shutil.rmtree(backup, ignore_errors=True)
        except OSError:
            pass

    def _install_omz(self) -> bool:
        """Step 2 — Oh My Zsh. git clone first (it never touches the shell),
        official installer only as a fallback."""
        if (OH_MY_ZSH / "oh-my-zsh.sh").exists():
            console.print("  [dim]Oh My Zsh already installed — updating...[/dim]")
            self._run_git(
                ["git", "-C", str(OH_MY_ZSH), "pull", "--quiet"],
                "Oh My Zsh update", timeout=PULL_TIMEOUT,
            )
            return True

        backup = self._salvage_broken_omz()

        if self._run_git(
            ["git", "clone", "--depth=1", OMZ_REPO, str(OH_MY_ZSH)],
            "Oh My Zsh clone", attempts=NET_RETRIES,
        ) and (OH_MY_ZSH / "oh-my-zsh.sh").exists():
            self._restore_omz_backup(backup)
            success_box("Oh My Zsh", "Installed successfully")
            return True

        console.print("  [warning]git clone failed — trying the official installer...[/warning]")
        try:
            result = run_cmd(
                ["sh", "-c",
                 f"RUNZSH=no CHSH=no KEEP_ZSHRC=yes sh -c \"$(curl -fsSL {OMZ_INSTALL_URL})\""],
                timeout=NET_TIMEOUT,
            )
            installer_ok = result.returncode == 0 and (OH_MY_ZSH / "oh-my-zsh.sh").exists()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            installer_ok = False

        if installer_ok:
            self._restore_omz_backup(backup)
            success_box("Oh My Zsh", "Installed via official installer")
            return True

        # Failed: put the previous state back (custom/ included) so a retry
        # can pick it up, and leave a clear error with the manual command
        self._restore_omz_backup(backup)
        error_box(
            "Oh My Zsh",
            "Install failed (slow network?).\n"
            f"  Retry later:  sw install shell\n"
            f"  Or manually:  git clone --depth=1 {OMZ_REPO} {OH_MY_ZSH}",
        )
        return False

    def _install_p10k(self) -> bool:
        """Step 3 — Powerlevel10k.

        The framework .zshrc sets ZSH_THEME="powerlevel10k/powerlevel10k", so
        p10k must be installed whenever ~/.oh-my-zsh exists — even when the
        OMZ install itself came from a partial/failed run.
        """
        if not OH_MY_ZSH.exists():
            console.print("  [dim]Oh My Zsh missing — skipping Powerlevel10k[/dim]")
            return False

        if (self.p10k_dir / P10K_THEME_FILE).exists():
            console.print("  [dim]Powerlevel10k already installed — updating...[/dim]")
            self._run_git(
                ["git", "-C", str(self.p10k_dir), "pull", "--quiet"],
                "Powerlevel10k update", timeout=PULL_TIMEOUT,
            )
            return True

        if self.p10k_dir.exists():
            # Half-cloned theme: git cannot clone into it
            console.print("  [warning]Powerlevel10k is incomplete — reinstalling...[/warning]")
            shutil.rmtree(self.p10k_dir, ignore_errors=True)

        if self._run_git(
            ["git", "clone", "--depth=1", P10K_REPO, str(self.p10k_dir)],
            "Powerlevel10k clone", attempts=NET_RETRIES,
        ) and (self.p10k_dir / P10K_THEME_FILE).exists():
            success_box("Powerlevel10k", "Installed successfully")
            return True

        shutil.rmtree(self.p10k_dir, ignore_errors=True)
        warning_box(
            "Powerlevel10k",
            "Clone failed — the theme falls back to robbyrussell.\n"
            f"  Retry later:  sw install shell\n"
            f"  Or manually:  git clone --depth=1 {P10K_REPO} {self.p10k_dir}",
        )
        return False

    def _install_plugins(self) -> tuple[int, int]:
        """Step 4 — plugins. Never fatal; returns (installed, failed)."""
        installed = 0
        failed = 0

        if not OH_MY_ZSH.exists():
            return 0, 0
        plugins_dir = OH_MY_ZSH / "custom" / "plugins"
        plugins_dir.mkdir(parents=True, exist_ok=True)

        groups = (
            [(n, r, True) for n, r in self.PLUGINS]
            + [(n, r, False) for n, r in self.OPTIONAL_PLUGINS]
        )
        for name, repo, required in groups:
            plugin_dir = plugins_dir / name
            if plugin_dir.exists() and (plugin_dir / ".git").exists():
                console.print(f"  [dim]Plugin {name} already installed[/dim]")
                continue
            if self._run_git(
                ["git", "clone", "--depth=1", repo, str(plugin_dir)],
                f"Plugin {name}", attempts=2,
            ):
                success_box("Plugin", f"{name} installed")
                installed += 1
            else:
                shutil.rmtree(plugin_dir, ignore_errors=True)
                failed += 1
                level = "warning" if required else "dim"
                note = "" if required else " (optional)"
                console.print(
                    f"  [{level}]Plugin {name} failed{note} — continuing without it[/{level}]"
                )
                if required:
                    console.print(f"  [dim]  Retry later: sw install shell[/dim]")
        return installed, failed

    def _ensure_default_shell(self) -> bool:
        """Step 5 — chsh. Runs even when p10k/plugins failed, so the user
        always lands in zsh on the next session."""
        if not cmd_exists("zsh"):
            return False

        current = run_cmd(["sh", "-c", "echo $SHELL"], capture=True).stdout.strip()
        zsh_path = shutil.which("zsh") or ""
        if current.endswith("/zsh") or (zsh_path and current == zsh_path):
            console.print("  [dim]zsh is already the default shell[/dim]")
            return True

        console.print("  [info]Setting zsh as default shell...[/info]")
        try:
            result = run_cmd(["chsh", "-s", "zsh"], timeout=60)
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            console.print(f"  [warning]chsh failed: {e}[/warning]")
            result = None

        if result is not None and result.returncode == 0:
            success_box("Shell", "zsh is now the default shell")
            return True

        console.print("  [warning]Could not change the default shell automatically.[/warning]")
        console.print("  [dim]Run manually: chsh -s zsh   (or just: exec zsh)[/dim]")
        return False

    # -----------------------------------------------------------
    # Module API
    # -----------------------------------------------------------
    def install(self) -> bool:
        try:
            info_box("Installing shell module", "Setting up zsh environment")

            # 1. zsh — the only fatal step
            if not self._install_zsh():
                error_box(
                    "Shell module",
                    "zsh could not be installed — fix the network and retry:\n"
                    "  sw install shell",
                )
                return False

            # 2. Oh My Zsh — failure is recoverable, keep going
            omz_ok = self._install_omz()

            # 3. Powerlevel10k — required by the framework theme; installed
            #    whenever ~/.oh-my-zsh exists, even after a failed OMZ step
            p10k_ok = self._install_p10k()

            # 4. Plugins — never fatal
            _installed, plugins_failed = self._install_plugins()

            # 5. chsh — must run even when the optional steps above failed
            self._ensure_default_shell()

            problems = []
            if not omz_ok:
                problems.append("Oh My Zsh")
            if not p10k_ok and omz_ok:
                problems.append("Powerlevel10k")
            if plugins_failed:
                problems.append(f"{plugins_failed} plugin(s)")

            if not problems:
                success_box("Shell module", "Installation complete!")
                return True

            warning_box(
                "Shell module",
                "Ready with warnings — missing: " + ", ".join(problems) + "\n"
                "  zsh works and the RICE will load. Repair the rest with: sw install shell",
            )
            return True

        except KeyboardInterrupt:
            info_box("Shell module", "Install cancelled")
            return False
        except Exception as e:
            error_box(
                "Shell module",
                f"Error: {e}\n"
                "  zsh may already be installed — retry with: sw install shell",
            )
            return False

    def uninstall(self) -> bool:
        info_box("Shell module", "Use: chsh -s bash to switch back")
        return True

    def update(self) -> bool:
        try:
            info_box("Updating shell module", "Pulling latest changes...")

            # A missing zsh/OMZ means the install never finished — repair it
            if not cmd_exists("zsh") or not OH_MY_ZSH.exists():
                info_box("Shell module", "Shell incomplete — running install to repair")
                return self.install()

            self._run_git(
                ["git", "-C", str(OH_MY_ZSH), "pull", "--quiet"],
                "Oh My Zsh", timeout=PULL_TIMEOUT,
            )
            self._install_p10k()

            plugins_dir = OH_MY_ZSH / "custom" / "plugins"
            if plugins_dir.exists():
                for plugin_dir in plugins_dir.iterdir():
                    if (plugin_dir / ".git").exists():
                        self._run_git(
                            ["git", "-C", str(plugin_dir), "pull", "--quiet"],
                            f"Plugin {plugin_dir.name}", timeout=PULL_TIMEOUT,
                        )

            success_box("Shell module", "Update complete!")
            return True

        except KeyboardInterrupt:
            info_box("Shell module", "Update cancelled")
            return False
        except Exception as e:
            error_box("Shell module", f"Error: {str(e)}")
            return False

    def status(self) -> dict:
        zsh = cmd_exists("zsh")
        omz = (OH_MY_ZSH / "oh-my-zsh.sh").exists()
        p10k = (self.p10k_dir / P10K_THEME_FILE).exists()

        if not zsh:
            return {"status": "missing", "details": "zsh: missing"}
        if omz and p10k:
            return {"status": "ok", "details": "zsh + Oh My Zsh + Powerlevel10k"}
        missing = [n for n, ok in (("Oh My Zsh", omz), ("Powerlevel10k", p10k)) if not ok]
        return {
            "status": "partial",
            "details": f"zsh ok — missing {', '.join(missing)} (sw install shell)",
        }
