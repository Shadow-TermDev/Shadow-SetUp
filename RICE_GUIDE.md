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

### TTS sin job control y alias agnósticos

Para que `la`/`ll`/`ls` (eza) siempre se registren y el TTS no imprima `[3] 24248` en el startup, añade al final de **cada** `rice.sh`:

```bash
# ── TTS sin job control (no imprime "[3] 24248") ──
if [[ "${SHADOW_TTS_ENABLED}" == "true" ]] && command -v termux-tts-speak &>/dev/null; then
  if [[ -n "${ZSH_VERSION:-}" ]]; then
    ( _h=$(date +%H); _g="Good evening"; (( _h >= 6 && _h < 12 )) && _g="Good morning"; (( _h >= 12 && _h < 19 )) && _g="Good afternoon"; termux-tts-speak -l "${SHADOW_TTS_LANG}" -r "${SHADOW_TTS_RATE}" "${_g}, ${SHADOW_TTS_MSG}" 2>/dev/null ) >/dev/null 2>&1 &! 2>/dev/null || true
  else
    nohup bash -c '_h=$(date +%H); _g="Good evening"; [ "$_h" -ge 6 ] && [ "$_h" -lt 12 ] && _g="Good morning"; [ "$_h" -ge 12 ] && [ "$_h" -lt 19 ] && _g="Good afternoon"; termux-tts-speak -l "'"${SHADOW_TTS_LANG}"'" -r "'"${SHADOW_TTS_RATE}"'" "${_g}, '"${SHADOW_TTS_MSG}"'" 2>/dev/null' >/dev/null 2>&1 & disown 2>/dev/null || true
  fi
fi

# ── Cargar alias/funciones del RICE de forma agnóstica ──
# Hace que active_rice.sh (copia de rice.sh) siempre registre ls/la/ll/tree
RICE_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" 2>/dev/null && pwd || cd "$(dirname "$0")" && pwd)"
[ -f "$RICE_SCRIPT_DIR/aliases.sh" ] && source "$RICE_SCRIPT_DIR/aliases.sh"
[ -f "$RICE_SCRIPT_DIR/functions.sh" ] && source "$RICE_SCRIPT_DIR/functions.sh"
if ! alias ls &>/dev/null; then
  [ -f "$HOME/.shadow-setup/aliases.sh" ] && source "$HOME/.shadow-setup/aliases.sh"
fi
```

Esto es el fix oficial para `nordic` y los rices `default`/`kawaii`/`term-shadow`. Si tu RICE no trae `aliases.sh`, el fallback carga los globales de `~/.shadow-setup/aliases.sh`. Incluir `font.ttf` con `install.font:true` en `manifest.json` evita verificar fuentes (como `term-shadow`).

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
