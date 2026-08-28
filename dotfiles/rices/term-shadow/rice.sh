#!/usr/bin/env bash
# ================================================
#  Shadow-SetUp · Term-Shadow RICE
#  The user's personal theme — argonaut colors,
#  JetBrains Mono, compact extra keys, cursor green
# ================================================

# Colors (Argonaut theme)
SHADOW_COLOR_PRIMARY="cyan"
SHADOW_COLOR_SECONDARY="magenta"
SHADOW_COLOR_ACCENT="green"

# Startup
SHADOW_STARTUP_MSG="Terminal lista"
SHADOW_STARTUP_ANIM=false

# TTS
SHADOW_TTS_ENABLED=false

# Environment
export SHADOW_RICE="term-shadow"
export BAT_THEME="ansi"
export PROMPT_EOL_MARK="|"

# Extra Termux settings
export TERMUX_EXTRA_KEYS="[[ 'ESC', '~', '/', 'HOME', 'UP', 'END', 'PGUP', 'TAB' ]]"
