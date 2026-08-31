# Shadow-SetUp

A modular Termux environment manager with a modern Python CLI and dynamic command system.

## Features

- **One-line install** — No need to clone the full repo
- **Hidden config** — All files stored in `~/.shadow-setup/`
- **Modular system** — Install only what you need
- **RICE system** — Complete themes with aliases, functions, and configs
- **Dynamic commands** — Each command is a separate file, auto-discovered at runtime
- **Dynamic TUI** — Menu generated from registered commands
- **Auto-updates** — Update from GitHub without reinstalling
- **MCP integration** — Agent integration via Model Context Protocol

## Quick Installation

```bash
curl -fsSL https://raw.githubusercontent.com/Shadow-TermDev/Shadow-SetUp/main/install.sh | bash
```

Then run:

```bash
sw help
```

## Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `sw install <module>` | `i` | Install a module |
| `sw update [module]` | `u` | Update module(s) |
| `sw uninstall <module>` | `rm` | Uninstall a module |
| `sw list` | `ls` | List available modules |
| `sw status [module]` | `st` | Show module status |
| `sw rice` | | Manage RICE themes |
| `sw update-core` | | Update framework from GitHub |
| `sw version` | `v` | Show version info |
| `sw help` | `--help`, `-h` | Show help |

### RICE Commands

| Command | Description |
|---------|-------------|
| `sw rice list` | List available RICEs |
| `sw rice set <name>` | Set active RICE |
| `sw rice set <name> -f` | Force reinstall RICE |
| `sw rice install <url>` | Install RICE from git |
| `sw rice update [name]` | Update RICE from git (all if no name) |
| `sw rice check` | Show active RICE |
| `sw rice delete <name>` | Delete local RICE |
| `sw rice backup <name>` | Backup current RICE |
| `sw rice reset` | Reset to default RICE |

> **Note:** `shadow` is also available as an alias for `sw`.

## Interactive Menu

Run `sw` with no arguments to open the TUI:

```
[1] Install module
[2] Update modules
[3] Uninstall module
[4] List modules
[5] System status
[6] Manage RICEs
[7] Update framework
[8] Version info
[x] Exit
```

## Modules

| Module | Description |
|--------|-------------|
| `shell` | zsh + Oh My Zsh + Powerlevel10k + plugins |
| `tools` | Essential packages (git, curl, bat, eza, fzf, etc.) |
| `fonts` | Nerd Fonts for Termux (with "keep current" option) |
| `dotfiles` | Configuration files (.zshrc, aliases, functions) |
| `aliases` | Shell aliases and functions |

## RICE System

RICEs are flexible theme packages. **Only `manifest.json` is required** — everything else is optional.

### RICE Structure

```
my-rice/
├── manifest.json          # REQUIRED — metadata + dependencies
├── rice.sh                # Sourced on every terminal startup
├── setup.sh               # Runs once on first apply
├── aliases.sh             # Shell aliases
├── functions.sh           # Shell functions
├── .p10k.zsh              # Powerlevel10k config
├── colors.properties      # Termux colors
├── font.ttf               # Termux font
├── termux.properties      # Termux settings
└── ...                    # Any files the creator wants
```

### manifest.json

```json
{
  "name": "my-rice",
  "version": "1.0.0",
  "author": "creator",
  "description": "...",
  "dependencies": {
    "packages": ["neofetch", "jq"],
    "pip": ["img2txt"],
    "omz_plugins": ["zsh-autosuggestions"]
  },
  "install": {
    "colors": true,
    "font": true,
    "termux_properties": true
  },
  "files": {
    "neofetch.conf": "~/.config/neofetch/config.conf"
  }
}
```

See [RICE_GUIDE.md](RICE_GUIDE.md) for the full specification.

### Official RICEs

| RICE | Theme | Description |
|------|-------|-------------|
| `term-shadow` | Argonaut | Personal theme — cyan/green, JetBrains Mono |
| `default` | Ocean | Clean theme — blue/white, Fira Code |
| `kawaii` | Pink Neon | Cute theme — magenta/pink, Hack Nerd Font |

### Custom RICEs

Install any RICE from a git repository:

```bash
sw rice install https://github.com/user/my-rice.git
```

## Project Structure

```
Shadow-SetUp/
├── .version                  # Version number
├── install.sh                # One-line installer
├── requirements.txt          # Python dependencies
├── LICENSE                   # MIT License
├── _lib/                     # CLI code
│   ├── __init__.py
│   ├── cli.py                # CLI entry point
│   ├── commands/             # Dynamic command system
│   │   ├── __init__.py       # Command base class + loader
│   │   ├── install.py
│   │   ├── update.py
│   │   ├── rice.py
│   │   └── ...
│   ├── modules/              # Installable modules
│   │   ├── shell.py
│   │   ├── tools.py
│   │   ├── fonts.py
│   │   ├── dotfiles.py
│   │   └── aliases.py
│   ├── utils/
│   │   ├── __init__.py       # run_cmd(), paths
│   │   ├── ui.py             # Rich + pyfiglet UI
│   │   └── rice_manager.py   # RICE download/apply/delete
│   └── mcp/                  # MCP server (agent integration)
│       ├── server.py
│       └── README.md
└── dotfiles/                 # Config files
    ├── .zshrc                # Minimal shell config
    ├── .nanorc
    ├── rices/                # RICE themes
    │   ├── manifest.json
    │   ├── term-shadow/
    │   ├── default/
    │   └── kawaii/
    └── active_rice.sh        # Symlink to active RICE
```

## Adding Custom Commands

Each command is a separate file in `_lib/commands/`:

```python
# _lib/commands/mycommand.py
from _lib.commands import Command

class MyCommand(Command):
    name = "mycommand"
    aliases = ["mc"]
    description = "My custom command"
    usage = "mycommand [args]"
    tui_label = "[9] My command"  # None = not in TUI
    tui_position = 90
    tui_section = "main"          # or "rice" for submenu

    def execute(self, args=None):
        from _lib.utils.ui import console, banner
        banner()
        console.print("Hello from my command!")
```

The command is auto-discovered and added to the TUI menu.

## Requirements

- Termux on Android
- Python 3.8+
- Git
- curl

### Python Dependencies

```
rich>=10.0.0
InquirerPy>=0.3.4
pyfiglet>=0.8.post1
```

## License

MIT
