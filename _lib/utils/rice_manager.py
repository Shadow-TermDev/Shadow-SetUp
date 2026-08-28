"""RICE manager — on-demand theme system for Shadow-SetUp."""

import json
import shutil
import subprocess
from pathlib import Path
from _lib.utils import SHADOW_DATA
from _lib.utils.ui import console, success_box, error_box, info_box, warning_box

RICES_DIR = SHADOW_DATA / "dotfiles" / "rices"
ACTIVE_RICE_LINK = SHADOW_DATA / "active_rice.sh"
BACKUP_DIR = SHADOW_DATA / "backups" / "rices"
MANIFEST_URL = "https://raw.githubusercontent.com/Shadow-TermDev/Shadow-SetUp/main/dotfiles/rices/manifest.json"
RICES_REPO_BASE = "https://github.com/Shadow-TermDev/rices"

def ensure_dirs():
    """Create RICE directories."""
    RICES_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def fetch_official_rices() -> dict:
    """Fetch official RICEs from manifest (local or remote)."""
    # Try local manifest first
    local_manifest = Path(__file__).parent.parent.parent / "dotfiles" / "rices" / "manifest.json"
    if local_manifest.exists():
        try:
            data = json.loads(local_manifest.read_text())
            return data.get("official_rices", {})
        except Exception:
            pass

    # Try remote manifest
    try:
        result = subprocess.run(
            ["curl", "-fsSL", MANIFEST_URL],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("official_rices", {})
    except Exception:
        pass

    # Fallback: minimal hardcoded list
    return {
        "default": {"description": "Clean, minimal theme", "url": RICES_REPO_BASE, "path": "default"},
        "kawaii": {"description": "Cute theme with TTS", "url": RICES_REPO_BASE, "path": "kawaii"},
        "cyberpunk": {"description": "Neon futuristic theme", "url": RICES_REPO_BASE, "path": "cyberpunk"},
        "minimal": {"description": "No animations, pure performance", "url": RICES_REPO_BASE, "path": "minimal"},
        "hacker": {"description": "Matrix-style green theme", "url": RICES_REPO_BASE, "path": "hacker"},
    }

def list_local_rices() -> list[dict]:
    """List locally installed RICEs."""
    ensure_dirs()
    rices = []

    for rice_dir in sorted(RICES_DIR.iterdir()):
        if rice_dir.is_dir():
            rice_sh = rice_dir / "rice.sh"
            rices.append({
                "name": rice_dir.name,
                "path": str(rice_dir),
                "has_script": rice_sh.exists(),
                "active": is_active(rice_dir.name),
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

def download_rice(rice_name: str, rice_info: dict) -> bool:
    """Download a RICE from GitHub."""
    ensure_dirs()

    rice_dir = RICES_DIR / rice_name
    if rice_dir.exists() and (rice_dir / "rice.sh").exists():
        return True  # Already downloaded

    url = rice_info.get("url", RICES_REPO_BASE)
    path = rice_info.get("path", rice_name)

    # Clone specific subdirectory using sparse checkout
    temp_dir = RICES_DIR / f".tmp_{rice_name}"
    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        # Shallow clone
        clone_url = f"{url}.git"
        result = subprocess.run(
            ["git", "clone", "--depth=1", "--filter=blob:none", "--sparse", clone_url, str(temp_dir)],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            error_box("Rice", f"Clone failed: {result.stderr.strip()}")
            return False

        # Sparse checkout for the specific rice
        result = subprocess.run(
            ["git", "-C", str(temp_dir), "sparse-checkout", "set", path],
            capture_output=True, text=True, timeout=10
        )

        if result.returncode != 0:
            # Fallback: try to copy entire repo
            pass

        # Move to final location
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

def apply_rice_files(rice_name: str) -> bool:
    """Copy RICE files to their destinations."""
    rice_dir = RICES_DIR / rice_name
    if not rice_dir.exists():
        return False

    try:
        # Copy rice.sh to active location
        rice_sh = rice_dir / "rice.sh"
        if rice_sh.exists():
            shutil.copy2(rice_sh, ACTIVE_RICE_LINK)

        # Copy .p10k.zsh if present
        p10k = rice_dir / ".p10k.zsh"
        if p10k.exists():
            shutil.copy2(p10k, Path.home() / ".p10k.zsh")

        # Copy Termux config files
        termux_dir = Path.home() / ".termux"
        termux_dir.mkdir(parents=True, exist_ok=True)

        for file_name in ["colors.properties", "font.ttf", "termux.properties"]:
            src = rice_dir / file_name
            if src.exists():
                shutil.copy2(src, termux_dir / file_name)

        # Reload Termux settings
        if subprocess.run(["command", "-v", "termux-reload-settings"], capture_output=True).returncode == 0:
            subprocess.run(["termux-reload-settings"], capture_output=True)

        return True

    except Exception as e:
        error_box("Rice", f"Apply failed: {e}")
        return False

def backup_current_rice(rice_name: str) -> bool:
    """Backup the current RICE before switching."""
    ensure_dirs()

    backup_file = BACKUP_DIR / f"{rice_name}.sh"
    try:
        if ACTIVE_RICE_LINK.exists():
            shutil.copy2(ACTIVE_RICE_LINK, backup_file)
            info_box("Rice", f"Backed up '{rice_name}'")
            return True
    except Exception as e:
        warning_box("Rice", f"Backup failed: {e}")

    return False

def download_and_apply_rice(rice_name: str, keep_backup: bool = True) -> bool:
    """Download (if needed) and apply a RICE."""
    ensure_dirs()

    # Fetch manifest
    official = fetch_official_rices()

    if rice_name in official:
        rice_info = official[rice_name]
    else:
        error_box("Rice", f"'{rice_name}' not found. Use 'sw rice install <url>' for custom RICEs.")
        return False

    # Backup current if switching
    active = get_active_rice()
    if active and active != rice_name and keep_backup:
        backup_current_rice(active)

    # Download
    console.print(f"  [cyan]Downloading '{rice_name}'...[/cyan]")
    if not download_rice(rice_name, rice_info):
        return False

    # Apply
    if not apply_rice_files(rice_name):
        return False

    success_box("Rice", f"'{rice_name}' activated")
    return True

def install_custom_rice(git_url: str) -> bool:
    """Install a custom RICE from a community Git URL."""
    ensure_dirs()

    # Extract name from URL
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

        if not (rice_dir / "rice.sh").exists():
            error_box("Rice", "No rice.sh found in repository")
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
