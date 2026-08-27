"""Shadow-SetUp — Modular Termux environment manager."""

from pathlib import Path

def _get_version():
    """Read version from .version file."""
    version_file = Path(__file__).parent.parent / ".version"
    if version_file.exists():
        return version_file.read_text().strip()
    return "2.2.0"

__version__ = _get_version()
__author__ = "Shadow-TermDev"
