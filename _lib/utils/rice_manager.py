"""RICE manager — flexible theme system for Shadow-SetUp.

RICE structure (only manifest.json is required):
    rice-name/
    ├── manifest.json      # Metadata + dependencies (REQUIRED)
    ├── rice.sh            # Sourced on terminal startup
    ├── setup.sh           # One-time setup (install deps, plugins)
    ├── aliases.sh         # Shell aliases
    ├── functions.sh       # Shell functions
    ├── .p10k.zsh          # Powerlevel10k config
    ├── colors.properties  # Termux colors
    ├── font.ttf           # Termux font
    ├── termux.properties  # Termux settings
    └── ...                # Any other files the creator wants

manifest.json schema:
    {
      "name": "my-rice",
      "version": "1.0.0",
      "author": "creator",
      "description": "...",
      "repo": "https://github.com/...",
      "dependencies": {
        "packages": ["neofetch", "image-cat"],
        "pip": ["img2txt"],
        "omz_plugins": ["zsh-autosuggestions"]
      },
      "install": {
        "colors": true,
        "font": true,
        "termux_properties": true
      },
      "files": {
        "custom.conf": "~/.config/app.conf",
        "script.sh": "~/.local/bin/myscript"
      }
    }
"""

import json
import shutil
import subprocess
from pathlib import Path
from _lib.utils import SHADOW_DATA, run_cmd, pkg_installed
from _lib.utils.ui import console, success_box, error_box, info_box, warning_box

RICES_DIR = SHADOW_DATA / "dotfiles" / "rices"
ACTIVE_RICE_LINK = SHADOW_DATA / "active_rice.sh"
BACKUP_DIR = SHADOW_DATA / "backups" / "rices"
INSTALLED_FILES_LOG = SHADOW_DATA / ".rice_installed_files"
MANIFEST_URL = "https://raw.githubusercontent.com/Shadow-TermDev/Shadow-SetUp/main/dotfiles/rices/manifest.json"
RICES_REPO_BASE = "https://github.com/Shadow-TermDev/rices"
TERMUX_HOME = Path.home() / ".termux"
SHADOW_BIN = Path.home() / ".local" / "bin"

# Default file mappings (when manifest doesn't specify "files")
DEFAULT_FILE_MAP = {
    "rice.sh": "active_rice.sh",
    "aliases.sh": "aliases.sh",
    "functions.sh": "functions.sh",
    ".p10k.zsh": "~/.p10k.zsh",
}

# Files that always go to ~/.termux/
TERMUX_FILES = {"colors.properties", "font.ttf", "termux.properties"}


def ensure_dirs():
    """Create RICE directories."""
    RICES_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def cleanup_previous_rice():
    """Remove files installed by the previous rice."""
    if not INSTALLED_FILES_LOG.exists():
        return

    try:
        lines = INSTALLED_FILES_LOG.read_text().strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            dst = Path(line)
            if dst.exists():
                if dst.is_file():
                    dst.unlink()
                elif dst.is_dir():
                    try:
                        dst.rmdir()
                    except OSError:
                        pass
        INSTALLED_FILES_LOG.unlink(missing_ok=True)
    except Exception:
        pass


def _track_installed_file(dst: Path):
    """Track a file that was installed by a rice for later cleanup."""
    INSTALLED_FILES_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(INSTALLED_FILES_LOG, "a") as f:
        f.write(str(dst) + "\n")


def _clear_tracking():
    """Clear the installed files tracking log."""
    if INSTALLED_FILES_LOG.exists():
        INSTALLED_FILES_LOG.unlink()


def load_manifest(rice_dir: Path) -> dict:
    """Load manifest.json from a RICE directory. Returns empty dict if missing."""
    manifest_path = rice_dir / "manifest.json"
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text())
        except (json.JSONDecodeError, Exception) as e:
            warning_box("Rice", f"Invalid manifest in {rice_dir.name}: {e}")
    return {}


def fetch_official_rices() -> dict:
    """Fetch official RICEs from manifest (local only)."""
    local_manifest = Path(__file__).parent.parent.parent / "dotfiles" / "rices" / "manifest.json"
    if local_manifest.exists():
        try:
            data = json.loads(local_manifest.read_text())
            return data.get("official_rices", {})
        except Exception:
            pass

    installed_manifest = RICES_DIR / "manifest.json"
    if installed_manifest.exists():
        try:
            data = json.loads(installed_manifest.read_text())
            return data.get("official_rices", {})
        except Exception:
            pass

    rices = {}
    if RICES_DIR.exists():
        for rice_dir in sorted(RICES_DIR.iterdir()):
            if rice_dir.is_dir():
                manifest = load_manifest(rice_dir)
                if manifest or (rice_dir / "rice.sh").exists():
                    rices[rice_dir.name] = {
                        "description": manifest.get("description", ""),
                        "local": True,
                    }
    return rices


def list_local_rices() -> list[dict]:
    """List locally installed RICEs."""
    ensure_dirs()
    rices = []

    for rice_dir in sorted(RICES_DIR.iterdir()):
        if rice_dir.is_dir():
            manifest = load_manifest(rice_dir)
            rices.append({
                "name": rice_dir.name,
                "path": str(rice_dir),
                "has_script": (rice_dir / "rice.sh").exists(),
                "active": is_active(rice_dir.name),
                "manifest": manifest,
            })

    return rices


def is_active(rice_name: str) -> bool:
    """Check if a RICE is currently active."""
    if not ACTIVE_RICE_LINK.exists():
        return False

    try:
        if ACTIVE_RICE_LINK.is_symlink():
            target = ACTIVE_RICE_LINK.resolve()
            rice_dir = RICES_DIR / rice_name
            return target.parent == rice_dir
        content = ACTIVE_RICE_LINK.read_text().strip()
        return rice_name in content
    except Exception:
        return False


def get_active_rice() -> str | None:
    """Get the name of the currently active RICE."""
    if not ACTIVE_RICE_LINK.exists():
        return None

    try:
        if ACTIVE_RICE_LINK.is_symlink():
            target = ACTIVE_RICE_LINK.resolve()
            return target.parent.name
        content = ACTIVE_RICE_LINK.read_text().strip()
        for rice_dir in RICES_DIR.iterdir():
            if rice_dir.name in content:
                return rice_dir.name
    except Exception:
        pass

    return None


def install_dependencies(rice_dir: Path) -> bool:
    """Install dependencies declared in manifest.json."""
    manifest = load_manifest(rice_dir)
    deps = manifest.get("dependencies", {})
    if not deps:
        return True

    installed_any = False

    # Termux packages
    packages = deps.get("packages", [])
    if packages:
        info_box("Dependencies", f"Installing {len(packages)} package(s)...")
        for pkg in packages:
            if pkg_installed(pkg):
                console.print(f"  [dim]{pkg} already installed[/dim]")
            else:
                console.print(f"  [info]Installing {pkg}...[/info]")
                result = run_cmd(["pkg", "install", "-y", pkg])
                if result.returncode == 0:
                    console.print(f"  [success]{pkg} installed[/success]")
                    installed_any = True
                else:
                    console.print(f"  [warning]Failed to install {pkg}[/warning]")

    # Python packages
    pip_packages = deps.get("pip", [])
    if pip_packages:
        info_box("Dependencies", f"Installing {len(pip_packages)} pip package(s)...")
        for pkg in pip_packages:
            console.print(f"  [info]Installing {pkg}...[/info]")
            result = run_cmd(["pip", "install", "--user", pkg])
            if result.returncode == 0:
                console.print(f"  [success]{pkg} installed[/success]")
                installed_any = True
            else:
                console.print(f"  [warning]Failed to install {pkg}[/warning]")

    # Oh My Zsh plugins
    omz_plugins = deps.get("omz_plugins", [])
    if omz_plugins:
        omz_dir = Path.home() / ".oh-my-zsh" / "custom" / "plugins"
        omz_dir.mkdir(parents=True, exist_ok=True)
        for plugin in omz_plugins:
            plugin_dir = omz_dir / plugin
            if plugin_dir.exists():
                console.print(f"  [dim]{plugin} already installed[/dim]")
                continue
            # Try common GitHub patterns for OMZ plugins
            console.print(f"  [info]Installing OMZ plugin: {plugin}...[/info]")
            urls = [
                f"https://github.com/zsh-users/{plugin}.git",
                f"https://github.com/zsh-users/zsh-{plugin}.git",
            ]
            cloned = False
            for url in urls:
                result = run_cmd(["git", "clone", "--depth=1", url, str(plugin_dir)], timeout=30)
                if result.returncode == 0:
                    console.print(f"  [success]{plugin} installed[/success]")
                    installed_any = True
                    cloned = True
                    break
            if not cloned:
                console.print(f"  [warning]Could not install {plugin} — add it manually[/warning]")

    return installed_any


def run_setup(rice_dir: Path) -> bool:
    """Run setup.sh if present (one-time setup)."""
    setup_script = rice_dir / "setup.sh"
    if not setup_script.exists():
        return True

    info_box("Setup", f"Running {rice_dir.name}/setup.sh...")
    try:
        result = subprocess.run(
            ["bash", str(setup_script)],
            capture_output=True, text=True, timeout=120,
            cwd=str(rice_dir),
        )
        if result.returncode == 0:
            if result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    console.print(f"  [dim]{line}[/dim]")
            success_box("Setup", "setup.sh completed")
            return True
        else:
            error_box("Setup", f"setup.sh failed: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        error_box("Setup", "setup.sh timed out (120s limit)")
        return False
    except Exception as e:
        error_box("Setup", f"setup.sh error: {e}")
        return False


def _selective_cleanup(rice_dir: Path, manifest: dict):
    """Remove only files that the new rice will replace.

    If new rice has font:false or no font.ttf, keep old font.
    Same for colors, termux_properties, .p10k.zsh, etc.
    """
    if not INSTALLED_FILES_LOG.exists():
        return

    install_cfg = manifest.get("install", {})
    custom_files = manifest.get("files", {})

    # Build set of destinations that new rice WILL write
    will_overwrite = set()

    # File map destinations
    file_map = dict(DEFAULT_FILE_MAP)
    file_map.update(custom_files)
    for src_name, dst_val in file_map.items():
        src = rice_dir / src_name
        if not src.exists():
            continue
        if dst_val == "active_rice.sh":
            will_overwrite.add(str(ACTIVE_RICE_LINK))
        elif dst_val == "aliases.sh":
            will_overwrite.add(str(SHADOW_DATA / "aliases.sh"))
        elif dst_val == "functions.sh":
            will_overwrite.add(str(SHADOW_DATA / "functions.sh"))
        elif dst_val.startswith("~/"):
            will_overwrite.add(str(Path.home() / dst_val[2:]))
        elif dst_val.startswith("/"):
            will_overwrite.add(str(Path(dst_val)))
        else:
            will_overwrite.add(str(SHADOW_DATA / dst_val))

    # Termux files (only if new rice provides them and manifest allows)
    if install_cfg.get("colors", True) and (rice_dir / "colors.properties").exists():
        will_overwrite.add(str(TERMUX_HOME / "colors.properties"))
    if install_cfg.get("font", True) and (rice_dir / "font.ttf").exists():
        will_overwrite.add(str(TERMUX_HOME / "font.ttf"))
    if install_cfg.get("termux_properties", True) and (rice_dir / "termux.properties").exists():
        will_overwrite.add(str(TERMUX_HOME / "termux.properties"))

    # Extra dirs
    SKIP_FILES = {"manifest.json", "setup.sh", "README.md", "LICENSE", "rices.sh", ".git", ".gitignore"}
    SKIP_PREFIXES = (".",)
    for item in rice_dir.iterdir():
        if item.name in SKIP_FILES:
            continue
        if any(item.name.startswith(p) for p in SKIP_PREFIXES):
            continue
        if item.is_dir():
            will_overwrite.add(str(SHADOW_DATA / item.name))

    # Only delete tracked files that new rice will overwrite
    try:
        lines = INSTALLED_FILES_LOG.read_text().strip().split("\n")
        remaining = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line in will_overwrite:
                dst = Path(line)
                if dst.exists():
                    if dst.is_file():
                        dst.unlink()
                    elif dst.is_dir():
                        try:
                            dst.rmdir()
                        except OSError:
                            pass
            else:
                remaining.append(line)

        # Keep remaining tracked files
        if remaining:
            INSTALLED_FILES_LOG.write_text("\n".join(remaining) + "\n")
        else:
            INSTALLED_FILES_LOG.unlink(missing_ok=True)
    except Exception:
        pass


def apply_rice_files(rice_dir: Path) -> bool:
    """Copy RICE files to their destinations based on manifest + defaults."""
    manifest = load_manifest(rice_dir)
    install_cfg = manifest.get("install", {})
    custom_files = manifest.get("files", {})

    try:
        # Selective cleanup: only remove files that new rice will replace
        _selective_cleanup(rice_dir, manifest)

        # Build full file map: custom overrides > defaults
        file_map = dict(DEFAULT_FILE_MAP)
        file_map.update(custom_files)

        # Apply file mappings
        for src_name, dst_val in file_map.items():
            src = rice_dir / src_name
            if not src.exists():
                continue

            # Resolve destination
            if dst_val == "active_rice.sh":
                dst = ACTIVE_RICE_LINK
            elif dst_val == "aliases.sh":
                dst = SHADOW_DATA / "aliases.sh"
            elif dst_val == "functions.sh":
                dst = SHADOW_DATA / "functions.sh"
            elif dst_val.startswith("~/"):
                dst = Path.home() / dst_val[2:]
            elif dst_val.startswith("/"):
                dst = Path(dst_val)
            else:
                dst = SHADOW_DATA / dst_val

            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            _track_installed_file(dst)

        # Apply Termux config files (unless manifest says not to)
        if install_cfg.get("colors", True):
            src = rice_dir / "colors.properties"
            if src.exists():
                TERMUX_HOME.mkdir(parents=True, exist_ok=True)
                dst = TERMUX_HOME / "colors.properties"
                shutil.copy2(src, dst)
                _track_installed_file(dst)

        if install_cfg.get("font", True):
            src = rice_dir / "font.ttf"
            if src.exists():
                TERMUX_HOME.mkdir(parents=True, exist_ok=True)
                dst = TERMUX_HOME / "font.ttf"
                shutil.copy2(src, dst)
                _track_installed_file(dst)

        if install_cfg.get("termux_properties", True):
            src = rice_dir / "termux.properties"
            if src.exists():
                TERMUX_HOME.mkdir(parents=True, exist_ok=True)
                dst = TERMUX_HOME / "termux.properties"
                shutil.copy2(src, dst)
                _track_installed_file(dst)

        # Apply any extra files in the RICE dir that aren't in the map
        # and aren't manifest/setup/metadata files
        SKIP_FILES = {
            "manifest.json", "setup.sh", "README.md", "LICENSE",
            "rices.sh", ".git", ".gitignore",
        }
        SKIP_PREFIXES = (".",)
        for item in rice_dir.iterdir():
            if item.name in SKIP_FILES:
                continue
            if any(item.name.startswith(p) for p in SKIP_PREFIXES):
                continue
            if item.is_dir():
                # Copy directories to ~/.shadow-setup/<name>/
                dst = SHADOW_DATA / item.name
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(item, dst)
                _track_installed_file(dst)

        # Reload Termux settings
        try:
            subprocess.run(["termux-reload-settings"], capture_output=True, timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return True

    except Exception as e:
        error_box("Rice", f"Apply failed: {e}")
        return False


def download_rice(rice_name: str, rice_info: dict) -> bool:
    """Download a RICE from GitHub (or copy if local)."""
    ensure_dirs()

    rice_dir = RICES_DIR / rice_name
    if rice_dir.exists() and ((rice_dir / "rice.sh").exists() or (rice_dir / "manifest.json").exists()):
        return True

    if rice_info.get("local"):
        possible_paths = [
            Path(__file__).parent.parent.parent / "dotfiles" / "rices" / rice_name,
            Path.home() / "Shadow-SetUp" / "dotfiles" / "rices" / rice_name,
            Path.home() / ".shadow-setup" / "dotfiles" / "rices" / rice_name,
        ]
        for repo_rice in possible_paths:
            if repo_rice.exists() and ((repo_rice / "manifest.json").exists() or (repo_rice / "rice.sh").exists()):
                shutil.copytree(repo_rice, rice_dir)
                return True
        error_box("Rice", f"Local RICE '{rice_name}' not found")
        return False

    # Remote RICEs — clone from git
    url = rice_info.get("url", RICES_REPO_BASE)
    path = rice_info.get("path", rice_name)
    temp_dir = RICES_DIR / f".tmp_{rice_name}"

    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        clone_url = f"{url}.git" if not url.endswith(".git") else url
        result = subprocess.run(
            ["git", "clone", "--depth=1", "--filter=blob:none", "--sparse", clone_url, str(temp_dir)],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            error_box("Rice", f"Clone failed: {result.stderr.strip()}")
            return False

        result = subprocess.run(
            ["git", "-C", str(temp_dir), "sparse-checkout", "set", path],
            capture_output=True, text=True, timeout=10
        )

        src = temp_dir / path
        if src.exists():
            if rice_dir.exists():
                shutil.rmtree(rice_dir)
            shutil.move(str(src), str(rice_dir))
        else:
            error_box("Rice", f"Rice '{rice_name}' not found in repo")
            return False

        shutil.rmtree(temp_dir)
        return True

    except subprocess.TimeoutExpired:
        error_box("Rice", "Download timed out")
        return False
    except Exception as e:
        error_box("Rice", f"Download failed: {e}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return False


def backup_current_rice(rice_name: str, ask: bool = True) -> bool:
    """Backup the current RICE before switching."""
    ensure_dirs()

    for old_backup in BACKUP_DIR.glob("*.sh"):
        old_backup.unlink()

    backup_file = BACKUP_DIR / f"{rice_name}.sh"

    if ask:
        try:
            from _lib.utils.ui import console
            result = console.input(f"  [bold]Backup current RICE '{rice_name}'? [Y/n]: [/bold]").strip()
            if result.lower() == "n":
                return True
        except (EOFError, KeyboardInterrupt):
            return True

    try:
        if ACTIVE_RICE_LINK.exists():
            shutil.copy2(ACTIVE_RICE_LINK, backup_file)
            info_box("Rice", f"Backed up '{rice_name}'")
            return True
    except Exception as e:
        warning_box("Rice", f"Backup failed: {e}")

    return False


def download_and_apply_rice(rice_name: str, keep_backup: bool = False, force: bool = False) -> bool:
    """Download (if needed) and apply a RICE."""
    ensure_dirs()

    rice_dir = RICES_DIR / rice_name

    if not force:
        is_downloaded = rice_dir.exists() and (
            (rice_dir / "rice.sh").exists() or (rice_dir / "manifest.json").exists()
        )
    else:
        is_downloaded = False
        if rice_dir.exists():
            shutil.rmtree(rice_dir)

    if is_downloaded:
        active = get_active_rice()
        if active and active != rice_name:
            backup_current_rice(active, ask=keep_backup)
        return _apply_existing_rice(rice_name)

    # Fetch manifest
    official = fetch_official_rices()

    if rice_name in official:
        rice_info = official[rice_name]
    else:
        error_box("Rice", f"'{rice_name}' not found. Use 'sw rice install <url>' for custom RICEs.")
        return False

    active = get_active_rice()
    if active and active != rice_name:
        backup_current_rice(active, ask=keep_backup)

    console.print(f"  [cyan]Downloading '{rice_name}'...[/cyan]")
    if not download_rice(rice_name, rice_info):
        return False

    return _apply_existing_rice(rice_name)


def _apply_existing_rice(rice_name: str) -> bool:
    """Apply an already-downloaded RICE: deps → setup → files."""
    rice_dir = RICES_DIR / rice_name

    # 1. Install dependencies
    install_dependencies(rice_dir)

    # 2. Run setup.sh (one-time)
    run_setup(rice_dir)

    # 3. Apply files
    if apply_rice_files(rice_dir):
        success_box("Rice", f"'{rice_name}' activated")
        console.print("[dim]Run [cyan]exec zsh[/cyan] or restart terminal to apply aliases.[/dim]")
        return True
    return False


def install_custom_rice(git_url: str) -> bool:
    """Install a custom RICE from a community Git URL."""
    ensure_dirs()

    repo_name = git_url.rstrip("/").split("/")[-1].replace(".git", "")
    rice_dir = RICES_DIR / repo_name

    if rice_dir.exists():
        warning_box("Rice", f"'{repo_name}' already exists, updating...")
        try:
            subprocess.run(["git", "-C", str(rice_dir), "pull"], capture_output=True, check=True)
            success_box("Rice", f"'{repo_name}' updated")
            return True
        except Exception as e:
            error_box("Rice", f"Update failed: {e}")
            return False

    try:
        result = subprocess.run(
            ["git", "clone", "--depth=1", git_url, str(rice_dir)],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            error_box("Rice", f"Clone failed: {result.stderr.strip()}")
            return False

        has_rice_sh = (rice_dir / "rice.sh").exists()
        has_manifest = (rice_dir / "manifest.json").exists()
        if not has_rice_sh and not has_manifest:
            error_box("Rice", "No rice.sh or manifest.json found in repository")
            shutil.rmtree(rice_dir)
            return False

        success_box("Rice", f"'{repo_name}' installed")
        return True

    except subprocess.TimeoutExpired:
        error_box("Rice", "Download timed out")
        return False
    except Exception as e:
        error_box("Rice", f"Installation failed: {e}")
        return False


def delete_rice(rice_name: str) -> bool:
    """Delete a local RICE."""
    rice_dir = RICES_DIR / rice_name

    if not rice_dir.exists():
        error_box("Rice", f"'{rice_name}' not found")
        return False

    if is_active(rice_name):
        error_box("Rice", "Can't delete active RICE. Switch first.")
        return False

    try:
        shutil.rmtree(rice_dir)
        success_box("Rice", f"'{rice_name}' deleted")
        return True
    except Exception as e:
        error_box("Rice", f"Delete failed: {e}")
        return False


def reset_rice_files() -> bool:
    """Reset to default rice. If default not found, just clear active rice."""
    cleanup_previous_rice()
    _clear_tracking()

    # Remove tracked termux/p10k files
    for f in ["colors.properties", "font.ttf", "termux.properties"]:
        p = TERMUX_HOME / f
        if p.exists():
            p.unlink()

    p10k = Path.home() / ".p10k.zsh"
    if p10k.exists():
        p10k.unlink()

    # Clear active rice
    if ACTIVE_RICE_LINK.exists():
        ACTIVE_RICE_LINK.unlink()

    # Try to restore default rice if available
    default_dir = RICES_DIR / "default"
    if default_dir.exists() and (default_dir / "rice.sh").exists():
        info_box("Rice", "Restoring default rice...")
        if apply_rice_files(default_dir):
            success_box("Rice", "Reset to default rice")
            return True

    # Fallback: copy base dotfiles
    base_zshrc = SHADOW_DATA / "dotfiles" / ".zshrc"
    if base_zshrc.exists():
        shutil.copy2(base_zshrc, Path.home() / ".zshrc")

    # Restore base termux config if available
    for fname in ["colors.properties", "termux.properties"]:
        src = SHADOW_DATA / "dotfiles" / ".termux" / fname
        if src.exists():
            TERMUX_HOME.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, TERMUX_HOME / fname)

    try:
        subprocess.run(["termux-reload-settings"], capture_output=True, timeout=5)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    success_box("Rice", "Reset complete — no active rice")
    return True


def update_rice(rice_name: str) -> bool:
    """Update a rice from its git repo (if it has .git)."""
    rice_dir = RICES_DIR / rice_name

    if not rice_dir.exists():
        error_box("Rice", f"'{rice_name}' not found")
        return False

    if not (rice_dir / ".git").exists():
        manifest = load_manifest(rice_dir)
        repo = manifest.get("repo", "")
        if repo:
            error_box("Rice", f"'{rice_name}' has no .git — reinstall: sw rice install {repo}")
        else:
            error_box("Rice", f"'{rice_name}' is a local rice (no git repo)")
        return False

    info_box("Rice", f"Updating '{rice_name}'...")
    try:
        result = subprocess.run(
            ["git", "-C", str(rice_dir), "pull", "--ff-only"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if "Already up to date" in output or "Already up-to-date" in output:
                success_box("Rice", f"'{rice_name}' already up to date")
            else:
                success_box("Rice", f"'{rice_name}' updated")
                # Re-apply if it's the active rice
                if is_active(rice_name):
                    info_box("Rice", "Re-applying active rice...")
                    apply_rice_files(rice_dir)
            return True
        else:
            error_box("Rice", f"Update failed: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        error_box("Rice", "Update timed out")
        return False
    except Exception as e:
        error_box("Rice", f"Update failed: {e}")
        return False
