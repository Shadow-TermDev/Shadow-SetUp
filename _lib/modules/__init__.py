"""Base module class for Shadow-SetUp."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

class BaseModule(ABC):
    """Base class for all Shadow-SetUp modules."""
    
    name: str = "base"
    description: str = "Base module"
    
    def __init__(self):
        self.home = Path.home()
        self.shadow_data = self.home / ".shadow-setup"
        self.cache_dir = self.shadow_data / "cache"
        
    @abstractmethod
    def install(self) -> bool:
        """Install the module. Returns True on success."""
        pass
    
    @abstractmethod
    def uninstall(self) -> bool:
        """Uninstall the module. Returns True on success."""
        pass
    
    @abstractmethod
    def update(self) -> bool:
        """Update the module. Returns True on success."""
        pass
    
    @abstractmethod
    def status(self) -> dict:
        """Return status information."""
        pass
    
    def is_installed(self) -> bool:
        """Check if module is installed."""
        return self.status().get("status") == "ok"
