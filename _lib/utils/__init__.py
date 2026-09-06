"""Utility functions for Shadow-SetUp CLI."""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional

# Paths — configs go to ~/.shadow-setup/
SHADOW_DATA = Path.home() / ".shadow-setup"
SHADOW_CACHE = SHADOW_DATA / "cache"
SHADOW_BACKUP = SHADOW_DATA / "backups"
SHADOW_BIN = Path.home() / ".local" / "bin"
TERMUX_HOME = Path.home() / ".termux"
OH_MY_ZSH = Path.home() / ".oh-my-zsh"

def ensure_dirs():
    """Create required directories."""
    SHADOW_DATA.mkdir(parents=True, exist_ok=True)
    SHADOW_CACHE.mkdir(parents=True, exist_ok=True)
    SHADOW_BACKUP.mkdir(parents=True, exist_ok=True)

def run_cmd(cmd: list[str], capture: bool = True, check: bool = False, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a shell command. Output hidden by default."""
    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        check=check,
        timeout=timeout
    )

def cmd_exists(cmd: str) -> bool:
    """Check if a command exists."""
    return shutil.which(cmd) is not None

# Cache for pkg list-installed to avoid 15 subprocess calls in tools.status() / sw help
# In-memory + filesystem persistent (TTL 5min) so `sw help` no ejecuta pkg cada vez
_PKG_CACHE: str | None = None
_PKG_CACHE_TIME: float = 0
_PKG_CACHE_TTL: float = 30  # segundos en memoria
_PKG_FILE_TTL: float = 300  # 5min en disco
_PKG_CACHE_FILE = SHADOW_DATA / "cache" / "pkg_cache.txt"
_PKG_CACHE_META = SHADOW_DATA / "cache" / "pkg_cache.meta"

def _load_pkg_cache_from_disk() -> tuple[str | None, float]:
    try:
        if _PKG_CACHE_FILE.exists() and _PKG_CACHE_META.exists():
            import time
            mtime = float(_PKG_CACHE_META.read_text().strip())
            if (time.time() - mtime) < _PKG_FILE_TTL:
                return _PKG_CACHE_FILE.read_text(), mtime
    except Exception:
        pass
    return None, 0

def _save_pkg_cache_to_disk(data: str):
    try:
        import time
        SHADOW_CACHE.mkdir(parents=True, exist_ok=True)
        _PKG_CACHE_FILE.write_text(data)
        _PKG_CACHE_META.write_text(str(time.time()))
    except Exception:
        pass

def pkg_installed(pkg: str) -> bool:
    """Check if a Termux package is installed (cached mem + disk)."""
    global _PKG_CACHE, _PKG_CACHE_TIME
    import time
    now = time.time()
    if _PKG_CACHE is None or (now - _PKG_CACHE_TIME) > _PKG_CACHE_TTL:
        # intentar disco primero
        disk_data, disk_time = _load_pkg_cache_from_disk()
        if disk_data is not None:
            _PKG_CACHE = disk_data
            _PKG_CACHE_TIME = disk_time
        else:
            try:
                result = run_cmd(["pkg", "list-installed"], capture=True, timeout=10)
                _PKG_CACHE = result.stdout if result.returncode == 0 else ""
                _PKG_CACHE_TIME = now
                _save_pkg_cache_to_disk(_PKG_CACHE or "")
            except Exception:
                _PKG_CACHE = ""
                _PKG_CACHE_TIME = now
    return f"{pkg}/" in (_PKG_CACHE or "")

def pkg_installed_many(pkgs: list[str]) -> dict[str, bool]:
    """Batch check multiple packages with single subprocess call (cached)."""
    global _PKG_CACHE, _PKG_CACHE_TIME
    import time
    now = time.time()
    if _PKG_CACHE is None or (now - _PKG_CACHE_TIME) > _PKG_CACHE_TTL:
        disk_data, disk_time = _load_pkg_cache_from_disk()
        if disk_data is not None:
            _PKG_CACHE = disk_data
            _PKG_CACHE_TIME = disk_time
        else:
            try:
                result = run_cmd(["pkg", "list-installed"], capture=True, timeout=10)
                _PKG_CACHE = result.stdout if result.returncode == 0 else ""
                _PKG_CACHE_TIME = now
                _save_pkg_cache_to_disk(_PKG_CACHE or "")
            except Exception:
                _PKG_CACHE = ""
                _PKG_CACHE_TIME = now
    out = _PKG_CACHE or ""
    return {p: f"{p}/" in out for p in pkgs}

def clear_pkg_cache():
    """Clear pkg cache (for testing or after install)."""
    global _PKG_CACHE, _PKG_CACHE_TIME
    _PKG_CACHE = None
    _PKG_CACHE_TIME = 0
    try:
        if _PKG_CACHE_FILE.exists():
            _PKG_CACHE_FILE.unlink()
        if _PKG_CACHE_META.exists():
            _PKG_CACHE_META.unlink()
    except Exception:
        pass

def backup_file(filepath: Path) -> Optional[Path]:
    """Backup a file before overwriting."""
    if filepath.exists():
        SHADOW_BACKUP.mkdir(parents=True, exist_ok=True)
        backup_path = SHADOW_BACKUP / filepath.name
        shutil.copy2(filepath, backup_path)
        return backup_path
    return None
