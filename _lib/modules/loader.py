"""Dynamic module loader — discovers modules at runtime."""

import pkgutil
import importlib
from pathlib import Path
from _lib.modules import BaseModule

_PACKAGE_DIR = Path(__file__).parent.parent / "modules"

def load_modules() -> dict[str, BaseModule]:
    """Auto-discover and instantiate all BaseModule subclasses in _lib/modules/."""
    modules = {}
    
    for importer, modname, ispkg in pkgutil.iter_modules([str(_PACKAGE_DIR)]):
        if modname.startswith("_") or modname == "base":
            continue
        
        try:
            full_name = f"_lib.modules.{modname}"
            mod = importlib.import_module(full_name)
            
            # Find the class that inherits from BaseModule
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseModule)
                    and attr is not BaseModule
                    and hasattr(attr, "name")
                    and attr.name != "base"
                ):
                    instance = attr()
                    modules[instance.name] = instance
                    break
        
        except Exception as e:
            # Skip modules that fail to load
            pass
    
    return modules

def get_module_names() -> list[str]:
    """Get list of available module names."""
    return sorted(load_modules().keys())
