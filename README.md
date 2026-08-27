# 🖤 Shadow-SetUp

A modular Termux environment manager with a modern Python CLI.

## Features

- **One-line install** — No need to clone the full repo
- **Hidden config** — All files stored in `~/.shadow-setup/`
- **Modular system** — Install only what you need
- **Dynamic UI** — Beautiful terminal output with Rich + pyfiglet
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
| `fonts` | Nerd Fonts for Termux (with "keep current" option) |
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
~/.shadow-setup/           ← Hidden config directory
├── _lib/                  ← CLI code
│   ├── __init__.py
│   ├── cli.py             ← CLI entry point
│   ├── modules/
│   │   ├── shell.py
│   │   ├── tools.py
│   │   ├── fonts.py
│   │   ├── dotfiles.py
│   │   └── aliases.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── ui.py          ← Rich + pyfiglet UI
│   └── mcp/
│       └── server.py      ← MCP server
├── dotfiles/               ← Config files
│   ├── .zshrc
│   ├── .p10k.zsh
│   ├── .nanorc
│   ├── aliases.sh
│   └── .termux/
└── cache/                  ← Temporary files
```

## Font Options

When installing the `fonts` module, you can choose:
- A new Nerd Font (jetbrains, fira, hack, iosevka, meslo)
- `keep` — Keep your current font unchanged

## MCP Server

Shadow-SetUp includes an MCP (Model Context Protocol) server for AI agent integration.

```bash
python3 ~/.shadow-setup/_lib/mcp/server.py
```

See [_lib/mcp/README.md](_lib/mcp/README.md) for details.

## Requirements

- Termux on Android
- Python 3.8+
- Git
- curl

## License

MIT
