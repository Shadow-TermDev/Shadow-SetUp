#!/usr/bin/env bash
# ================================================
#  Shadow-SetUp · Term-Shadow RICE
#  Personal theme — argonaut colors,
#  JetBrains Mono, compact extra keys, cursor green
# ================================================

# Colors (Argonaut theme)
SHADOW_COLOR_PRIMARY="cyan"
SHADOW_COLOR_SECONDARY="magenta"
SHADOW_COLOR_ACCENT="green"

# Startup
SHADOW_STARTUP_MSG="Starting terminal..."
SHADOW_STARTUP_ANIM=true

# TTS
SHADOW_TTS_ENABLED=true
SHADOW_TTS_LANG="en-US"
SHADOW_TTS_RATE="1.1"
SHADOW_TTS_MSG="Good evening, terminal ready, let's code"

# Environment
export SHADOW_RICE="term-shadow"
export BAT_THEME="ansi"
export PROMPT_EOL_MARK="|"

# Startup animation
if [[ "$SHADOW_STARTUP_ANIM" == "true" ]]; then
    mensaje="$SHADOW_STARTUP_MSG"
    color='\033[92m'
    fin_color='\033[0m'
    for ((i=0; i<${#mensaje}; i++)); do
        echo -ne "${color}${mensaje:$i:1}${fin_color}"
        sleep 0.15
    done
    echo
    sleep 0.3
fi

# TTS greeting
if [[ "$SHADOW_TTS_ENABLED" == "true" ]] && command -v termux-tts-speak &>/dev/null; then
    nohup sh -c "
        h=\$(date +%H)
        g='Good evening'
        [ \"\$h\" -ge 6 ] && [ \"\$h\" -lt 12 ] && g='Good morning'
        [ \"\$h\" -ge 12 ] && [ \"\$h\" -lt 19 ] && g='Good afternoon'
        termux-tts-speak -l ${SHADOW_TTS_LANG} -r ${SHADOW_TTS_RATE} \"\${g}, terminal ready, let's code\"
    " &>/dev/null &!
fi

# ── Cargar alias/funciones del RICE de forma agnóstica ──
RICE_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" 2>/dev/null && pwd || cd "$(dirname "$0")" && pwd)"
[ -f "$RICE_SCRIPT_DIR/aliases.sh" ] && source "$RICE_SCRIPT_DIR/aliases.sh"
[ -f "$RICE_SCRIPT_DIR/functions.sh" ] && source "$RICE_SCRIPT_DIR/functions.sh"
if ! alias ls &>/dev/null; then
    [ -f "$HOME/.shadow-setup/aliases.sh" ] && source "$HOME/.shadow-setup/aliases.sh"
fi
