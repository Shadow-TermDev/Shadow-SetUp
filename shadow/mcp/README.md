# Shadow-SetUp MCP

MCP (Model Context Protocol) server for Shadow-SetUp agent integration.

## Usage

### As a stdio MCP server

```bash
python3 shadow/mcp/server.py
```

### With Claude Code or other MCP clients

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "shadow-setup": {
      "command": "python3",
      "args": ["/path/to/Shadow-SetUp/shadow/mcp/server.py"]
    }
  }
}
```

## Available Tools

### `shadow_install`
Install a Shadow-SetUp module.

**Parameters:**
- `module` (string, required): Module name (shell, tools, fonts, dotfiles, aliases)

### `shadow_update`
Update Shadow-SetUp modules or core.

**Parameters:**
- `module` (string, optional): Module name or 'core' to update framework

### `shadow_status`
Get status of Shadow-SetUp modules.

**Parameters:**
- `module` (string, optional): Module name (shows all if not specified)

### `shadow_list_modules`
List all available Shadow-SetUp modules.

**Parameters:** None

### `shadow_get_config`
Get Shadow-SetUp configuration.

**Parameters:**
- `key` (string, optional): Configuration key (home, cache, backup)

## Example Agent Integration

```python
import subprocess
import json

# Start MCP server
proc = subprocess.Popen(
    ["python3", "shadow/mcp/server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# List modules
request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
proc.stdin.write(json.dumps(request) + "\n")
proc.stdin.flush()

response = json.loads(proc.stdout.readline())
print(response["result"]["tools"])
```

## Technical Notes

### Banner Rendering

Shadow-SetUp uses **pyfiglet** for ASCII art banners instead of hardcoded text. Benefits:

- **Token efficiency** — pyfiglet generates banners dynamically, no need to embed large ASCII art in code or prompts
- **No visual bugs** — manual ASCII art can have alignment issues across different fonts/terminals; pyfiglet handles this automatically
- **Zoom adaptive** — different fonts are used based on terminal width (slant/standard/small)
- **Fallback safe** — if pyfiglet fails, a plain text fallback is used

**Recommended pyfiglet fonts for CLI tools:**
- `slant` — Clean, modern look for large terminals
- `standard` — Classic ASCII art for medium terminals
- `small` — Compact for small terminals
- `banner3` — Tall, impactful banners
- `big` — Bold, readable text

**Why not hardcoded ASCII art?**
1. Hardcoded banners consume more tokens when included in AI prompts/context
2. Manual alignment is error-prone and can break with different terminal fonts
3. ASCII art requires manual updates if the project name changes
4. pyfiglet supports 300+ fonts, making it easy to change the look without code changes

### Dependencies

- `rich` — Terminal UI components (panels, tables, progress bars)
- `pyfiglet` — ASCII art font rendering
- `colorama` — Cross-platform colored output (optional, Rich handles most cases)
