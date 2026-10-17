"""Dynamic module loader — discovers modules at runtime."""

import pkgutil
import importlib
from pathlib import Path
from _lib.modules import BaseModule

_PACKAGE_DIR = Path(__file__).parent.parent / "modules"

# Load failures (module name, reason) — surfaced to the user instead of failing silently
MODULE_LOAD_ERRORS: list[tuple[str, str]] = []

def load_modules() -> dict[str, BaseModule]:
    """Auto-discover and instantiate all BaseModule subclasses in _lib/modules/."""
    global MODULE_LOAD_ERRORS
    modules = {}
    MODULE_LOAD_ERRORS = []

    for importer, modname, ispkg in pkgutil.iter_modules([str(_PACKAGE_DIR)]):
        if modname.startswith("_") or modname == "base":
            continue
        
        try:
            full_name = f"_lib.modules.{modname}"
            mod = importlib.import_module(full_name)
            
            # Find the class that inherits from BaseModule
            found = False
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
                    found = True
                    break

            if not found:
                MODULE_LOAD_ERRORS.append((modname, "no BaseModule subclass found"))

        except Exception as e:
            import warnings
            warnings.warn(f"Failed to load module '{modname}': {e}", stacklevel=2)
            MODULE_LOAD_ERRORS.append((modname, str(e)))
    
    return modules

def get_module_load_errors() -> list[tuple[str, str]]:
    """Modules that failed to load (name, reason)."""
    return [err for err in MODULE_LOAD_ERRORS]

def get_module_names() -> list[str]:
    """Get list of available module names."""
    return sorted(load_modules().keys())
