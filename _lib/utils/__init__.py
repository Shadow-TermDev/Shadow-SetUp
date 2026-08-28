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

def run_cmd(cmd: list[str], capture: bool = True, check: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command. Output hidden by default."""
    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        check=check
    )

def cmd_exists(cmd: str) -> bool:
    """Check if a command exists."""
    return shutil.which(cmd) is not None

def pkg_installed(pkg: str) -> bool:
    """Check if a Termux package is installed."""
    result = run_cmd(["pkg", "list-installed"], capture=True)
    return f"{pkg}/" in result.stdout

def get_terminal_size() -> tuple[int, int]:
    """Get terminal columns and rows."""
    size = shutil.get_terminal_size()
    return size.columns, size.lines

def backup_file(filepath: Path) -> Optional[Path]:
    """Backup a file before overwriting."""
    if filepath.exists():
        SHADOW_BACKUP.mkdir(parents=True, exist_ok=True)
        backup_path = SHADOW_BACKUP / filepath.name
        shutil.copy2(filepath, backup_path)
        return backup_path
    return None
