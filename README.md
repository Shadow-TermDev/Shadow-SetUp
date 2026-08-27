# 🖤 Shadow-SetUp

A modular Termux environment manager with a modern Python CLI.

## Features

- **One-line install** — No need to clone the full repo
- **Modular system** — Install only what you need
- **Dynamic UI** — Beautiful terminal output with Rich
- **MCP server** — AI agent integration
- **Auto-updates** — Update from GitHub without reinstalling

## Quick Installation

```bash
curl -fsSL https://raw.githubusercontent.com/Shadow-TermDev/Shadow-SetUp/main/install.sh | bash
```

Then run:

```bash
sw help
```

## Commands

| Command | Description |
|---------|-------------|
| `sw install <module>` | Install a module |
| `sw update [module]` | Update module(s) |
| `sw uninstall <module>` | Uninstall a module |
| `sw list` | List available modules |
| `sw status [module]` | Show module status |
| `sw update-core` | Update framework from GitHub |
| `sw version` | Show version |

> **Note:** `shadow` is also available as an alias for `sw`.

## Modules

| Module | Description |
|--------|-------------|
| `shell` | zsh + Oh My Zsh + Powerlevel10k + plugins |
| `tools` | Essential packages (git, curl, bat, eza, fzf, etc.) |
| `fonts` | Nerd Fonts for Termux |
| `dotfiles` | Configuration files (.zshrc, .p10k.zsh, .nanorc) |
| `aliases` | Shell aliases and functions |

## Examples

```bash
# Install everything
sw install shell tools fonts dotfiles aliases

# Install just shell
sw install shell

# Update all modules
sw update

# Update only shell
sw update shell

# Check status
sw status

# Update framework
sw update-core
```

## Project Structure

```
Shadow-SetUp/
├── install.sh              ← curl-installable installer
├── sw                      ← CLI wrapper (short alias)
├── shadow/
│   ├── __init__.py
│   ├── cli.py              ← CLI entry point
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── shell.py
│   │   ├── tools.py
│   │   ├── fonts.py
│   │   ├── dotfiles.py
│   │   └── aliases.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── ui.py           ← Rich-based UI
│   └── mcp/
│       ├── __init__.py
│       ├── server.py       ← MCP server
│       └── README.md
├── dotfiles/
│   ├── .zshrc
│   ├── .p10k.zsh
│   ├── .nanorc
│   ├── aliases.sh
│   └── .termux/
│       ├── colors.properties
│       ├── font.ttf
│       └── termux.properties
└── README.md
```

## MCP Server

Shadow-SetUp includes an MCP (Model Context Protocol) server for AI agent integration.

```bash
# Start MCP server
python3 shadow/mcp/server.py
```

See [shadow/mcp/README.md](shadow/mcp/README.md) for details.

## Requirements

- Termux on Android
- Python 3.8+
- Git
- curl

## License

MIT
