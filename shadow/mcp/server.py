"""MCP Server for Shadow-SetUp — Agent integration."""

import json
import sys
from pathlib import Path
from typing import Any

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shadow.modules.shell import ShellModule
from shadow.modules.tools import ToolsModule
from shadow.modules.fonts import FontsModule
from shadow.modules.dotfiles import DotfilesModule
from shadow.modules.aliases import AliasesModule
from shadow.utils import SHADOW_HOME

MODULES = {
    "shell": ShellModule(),
    "tools": ToolsModule(),
    "fonts": FontsModule(),
    "dotfiles": DotfilesModule(),
    "aliases": AliasesModule(),
}

# MCP Protocol handlers
def handle_initialize(params: dict) -> dict:
    """Handle MCP initialize request."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {},
            "resources": {}
        },
        "serverInfo": {
            "name": "shadow-setup",
            "version": "2.0.0"
        }
    }

def handle_tools_list(params: dict) -> dict:
    """List available tools."""
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
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "shadow_get_config",
                "description": "Get Shadow-SetUp configuration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "Configuration key (home, cache, backup)"
                        }
                    }
                }
            }
        ]
    }

def handle_tools_call(params: dict) -> dict:
    """Handle tool calls."""
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
                # Update core from GitHub
                from shadow.utils.ui import update_core
                update_core()
                return {"success": True, "message": "Core updated"}
            elif module_name in MODULES:
                result = MODULES[module_name].update()
                return {"success": result, "module": module_name}
            elif module_name is None:
                # Update all
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
                "home": str(SHADOW_HOME),
                "cache": str(SHADOW_HOME.parent / ".cache" / "shadow-setup"),
                "backup": str(SHADOW_HOME.parent / ".shadow-backup"),
            }
            if key:
                return {key: config.get(key)}
            return config
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    except Exception as e:
        return {"error": str(e)}

def main():
    """Main MCP server loop."""
    # Simple JSON-RPC over stdin/stdout
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
            
            # Send response
            result = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": response
            }
            print(json.dumps(result))
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -1, "message": str(e)}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
