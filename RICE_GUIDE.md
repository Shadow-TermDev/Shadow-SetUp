# Creating RICEs for Shadow-SetUp

A RICE is a complete terminal theme package. **Only `manifest.json` is required** — everything else is optional and up to you.

## Minimum RICE

```
my-rice/
└── manifest.json
```

That's it. The framework will detect it and apply it.

## Full RICE Example

```
my-rice/
├── manifest.json          # REQUIRED — metadata + dependencies
├── rice.sh                # Sourced on every terminal startup
├── setup.sh               # Runs once when RICE is first applied
├── aliases.sh             # Shell aliases
├── functions.sh           # Shell functions
├── .p10k.zsh              # Powerlevel10k prompt config
├── colors.properties      # Termux color scheme
├── font.ttf               # Termux font
├── termux.properties      # Termux settings (extra keys, cursor, etc.)
├── neofetch.conf          # Your neofetch config
├── fastfetch/             # Your fastfetch config
├── scripts/               # Any scripts you want to include
│   └── my-tool.sh
└── .config/               # Any app configs
    └── my-app.conf
```

## manifest.json Schema

```json
{
  "name": "my-rice",
  "version": "1.0.0",
  "author": "your-github-username",
  "description": "Short description of your theme",
  "repo": "https://github.com/you/my-rice",

  "dependencies": {
    "packages": ["neofetch", "jq", "fzf"],
    "pip": ["img2txt", "rich"],
    "omz_plugins": ["zsh-autosuggestions"]
  },

  "install": {
    "colors": true,
    "font": true,
    "termux_properties": true
  },

  "files": {
    ".p10k.zsh": "~/.p10k.zsh",
    "neofetch.conf": "~/.config/neofetch/config.conf",
    "scripts/my-tool.sh": "~/.local/bin/my-tool"
  }
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | RICE name (should match directory name) |
| `version` | No | Semantic version |
| `author` | No | Your GitHub username |
| `description` | No | Short description |
| `repo` | No | URL to your RICE repository |
| `dependencies` | No | Packages to auto-install |
| `install` | No | Which Termux config files to apply |
| `files` | No | Custom file mappings (source → destination) |

### dependencies

```json
"dependencies": {
  "packages": ["neofetch"],     // pkg install <package>
  "pip": ["img2txt"],           // pip install --user <package>
  "omz_plugins": ["plugin"]    // git clone into ~/.oh-my-zsh/custom/plugins/
}
```

### install

Controls which standard Termux config files get copied:

```json
"install": {
  "colors": true,          // colors.properties → ~/.termux/colors.properties
  "font": true,            // font.ttf → ~/.termux/font.ttf
  "termux_properties": true // termux.properties → ~/.termux/termux.properties
}
```

Set any to `false` to skip copying that file.

### files

Map any file in your RICE to any destination:

```json
"files": {
  "source_file": "destination",

  // Special destinations:
  "rice.sh": "active_rice.sh",      // → ~/.shadow-setup/active_rice.sh
  "aliases.sh": "aliases.sh",       // → ~/.shadow-setup/aliases.sh
  "functions.sh": "functions.sh",   // → ~/.shadow-setup/functions.sh

  // Home directory:
  ".p10k.zsh": "~/.p10k.zsh",

  // Absolute paths:
  "my.conf": "/etc/my.conf",

  // Relative to ~/.shadow-setup/:
  "script.sh": "scripts/my-script.sh"
}
```

Files NOT in the map are automatically copied to `~/.shadow-setup/<name>/`.

## setup.sh

Runs **once** when the RICE is first applied. Use it for:

- Installing dependencies not handled by manifest
- Cloning plugins
- Compiling tools
- Any one-time setup

```bash
#!/usr/bin/env bash
# setup.sh — runs once on first apply

echo "Setting up my-rice..."

# Example: install a custom tool
if ! command -v my-tool &>/dev/null; then
    git clone --depth=1 https://github.com/me/my-tool.git ~/my-tool
    ln -sf ~/my-tool/bin/my-tool ~/.local/bin/my-tool
fi

# Example: compile something
# make -C ~/my-project

echo "Setup complete!"
```

## rice.sh

Sourced on **every** terminal startup. Use it for:

- Setting environment variables
- Startup animation
- TTS greeting
- Theme colors

```bash
#!/usr/bin/env bash
# rice.sh — sourced on every terminal startup

# Colors
SHADOW_COLOR_PRIMARY="cyan"
SHADOW_COLOR_SECONDARY="magenta"

# Startup message
SHADOW_STARTUP_MSG="Welcome back!"
SHADOW_STARTUP_ANIM=true

# TTS
SHADOW_TTS_ENABLED=true
SHADOW_TTS_LANG="en-US"
SHADOW_TTS_MSG="Terminal ready"

# Environment
export SHADOW_RICE="my-rice"
export BAT_THEME="Monokai Extended"
```

## Managing RICEs

```bash
sw rice list                      # List all available RICEs
sw rice set <name>                # Activate a RICE
sw rice set <name> -f             # Force reinstall
sw rice update <name>             # Update from git (re-applies if active)
sw rice update                    # Update all installed RICEs
sw rice check                     # Show active RICE
sw rice reset                     # Reset to default RICE
sw rice delete <name>             # Delete a local RICE
```

## Publishing Your RICE

1. Create a GitHub repo with your RICE files
2. Make sure `manifest.json` is in the root (or in a subdirectory)
3. Users can install it with:

```bash
sw rice install https://github.com/you/my-rice.git
```

Or for RICEs in a subdirectory:

```bash
sw rice install https://github.com/you/rice-collection.git my-rice
```

Keep your RICE updated:

```bash
sw rice update my-rice            # Pull latest from git
```

## Tips

- **Test with `sw rice set <name>`** after making changes
- **`setup.sh` only runs once** — delete `~/.shadow-setup/dotfiles/rices/<name>/.setup_done` to re-run
- **Use `command -v`** to check if tools are available before using them
- **Keep `rice.sh` fast** — it runs on every terminal open
- **Use `setup.sh` for heavy work** — it only runs once
- **Include a `README.md`** in your RICE repo to document it
