"""MCP Server for Shadow-SetUp — Agent integration."""

import json
import sys
from pathlib import Path

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from _lib.modules.shell import ShellModule
from _lib.modules.tools import ToolsModule
from _lib.modules.fonts import FontsModule
from _lib.modules.dotfiles import DotfilesModule
from _lib.modules.aliases import AliasesModule
from _lib.utils import SHADOW_DATA

MODULES = {
    "shell": ShellModule(),
    "tools": ToolsModule(),
    "fonts": FontsModule(),
    "dotfiles": DotfilesModule(),
    "aliases": AliasesModule(),
}

def bump_version(bump_type: str = "patch") -> str:
    """Bump version in .version file."""
    version_file = Path(__file__).parent.parent.parent / ".version"
    if not version_file.exists():
        return "0.0.1"
    
    version = version_file.read_text().strip()
    parts = version.split(".")
    if len(parts) != 3:
        return "0.0.1"
    
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    if bump_type == "major":
        major += 1; minor = 0; patch = 0
    elif bump_type == "minor":
        minor += 1; patch = 0
    else:
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    version_file.write_text(new_version + "\n")
    return new_version

def handle_initialize(params: dict) -> dict:
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}, "resources": {}},
        "serverInfo": {"name": "shadow-setup", "version": "2.1.0"}
    }

def handle_tools_list(params: dict) -> dict:
    return {
        "tools": [
            {
                "name": "shadow_install",
                "description": "Install a Shadow-SetUp module",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "module": {
                            "type": "string",
                            "description": "Module name (shell, tools, fonts, dotfiles, aliases)"
                        }
                    },
                    "required": ["module"]
                }
            },
            {
                "name": "shadow_update",
                "description": "Update Shadow-SetUp modules or core",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "module": {
                            "type": "string",
                            "description": "Module name or 'core' to update framework"
                        }
                    }
                }
            },
            {
                "name": "shadow_status",
                "description": "Get status of Shadow-SetUp modules",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "module": {
                            "type": "string",
                            "description": "Module name (optional, shows all if not specified)"
                        }
                    }
                }
            },
            {
                "name": "shadow_list_modules",
                "description": "List all available Shadow-SetUp modules",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "shadow_get_config",
                "description": "Get Shadow-SetUp configuration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "Configuration key (data, cache, backup)"
                        }
                    }
                }
            },
            {
                "name": "shadow_bump_version",
                "description": "Bump version in .version file (call before commit/push)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["major", "minor", "patch"],
                            "description": "Version bump type (default: patch)"
                        }
                    }
                }
            }
        ]
    }

def handle_tools_call(params: dict) -> dict:
    tool_name = params.get("name", "")
    arguments = params.get("arguments", {})
    
    try:
        if tool_name == "shadow_install":
            module_name = arguments.get("module")
            if module_name not in MODULES:
                return {"error": f"Unknown module: {module_name}"}
            result = MODULES[module_name].install()
            return {"success": result, "module": module_name}
        
        elif tool_name == "shadow_update":
            module_name = arguments.get("module")
            if module_name == "core":
                from _lib.utils.ui import console
                from _lib.cli import update_core
                update_core()
                return {"success": True, "message": "Core updated"}
            elif module_name in MODULES:
                result = MODULES[module_name].update()
                return {"success": result, "module": module_name}
            elif module_name is None:
                results = {}
                for name, mod in MODULES.items():
                    results[name] = mod.update()
                return {"success": True, "results": results}
            else:
                return {"error": f"Unknown module: {module_name}"}
        
        elif tool_name == "shadow_status":
            module_name = arguments.get("module")
            if module_name:
                if module_name not in MODULES:
                    return {"error": f"Unknown module: {module_name}"}
                return {module_name: MODULES[module_name].status()}
            else:
                return {name: mod.status() for name, mod in MODULES.items()}
        
        elif tool_name == "shadow_list_modules":
            return {
                "modules": {
                    name: {"description": mod.description}
                    for name, mod in MODULES.items()
                }
            }
        
        elif tool_name == "shadow_get_config":
            key = arguments.get("key")
            config = {
                "data": str(SHADOW_DATA),
                "cache": str(SHADOW_DATA / "cache"),
                "backup": str(SHADOW_DATA / "backups"),
            }
            if key:
                return {key: config.get(key)}
            return config
        
        elif tool_name == "shadow_bump_version":
            bump_type = arguments.get("type", "patch")
            new_version = bump_version(bump_type)
            return {"success": True, "version": new_version}
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    except Exception as e:
        return {"error": str(e)}

def main():
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get("method", "")
            params = request.get("params", {})
            req_id = request.get("id")
            
            if method == "initialize":
                response = handle_initialize(params)
            elif method == "tools/list":
                response = handle_tools_list(params)
            elif method == "tools/call":
                response = handle_tools_call(params)
            else:
                response = {"error": f"Unknown method: {method}"}
            
            result = {"jsonrpc": "2.0", "id": req_id, "result": response}
            print(json.dumps(result))
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {"jsonrpc": "2.0", "id": None, "error": {"code": -1, "message": str(e)}}
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
