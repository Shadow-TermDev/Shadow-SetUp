"""Utility functions for Shadow-SetUp CLI."""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional

# Paths
SHADOW_HOME = Path.home() / "Shadow-SetUp"
SHADOW_CACHE = Path.home() / ".cache" / "shadow-setup"
SHADOW_BACKUP = Path.home() / ".shadow-backup"
TERMUX_HOME = Path.home() / ".termux"
OH_MY_ZSH = Path.home() / ".oh-my-zsh"

def ensure_dirs():
    """Create required directories."""
    SHADOW_CACHE.mkdir(parents=True, exist_ok=True)
    SHADOW_BACKUP.mkdir(parents=True, exist_ok=True)

def run_cmd(cmd: list[str], capture: bool = False, check: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command."""
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
        backup_dir = SHADOW_BACKUP / "latest"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / filepath.name
        shutil.copy2(filepath, backup_path)
        return backup_path
    return None
