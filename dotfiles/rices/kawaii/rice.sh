#!/usr/bin/env bash
# ================================================
#  Shadow-SetUp · Kawaii RICE
#  Pink Neon theme — magenta/pink, Hack Nerd Font
# ================================================

# Colors (Pink Neon theme)
SHADOW_COLOR_PRIMARY="magenta"
SHADOW_COLOR_SECONDARY="pink"
SHADOW_COLOR_ACCENT="yellow"

# Startup
SHADOW_STARTUP_MSG="Onii-chan, terminal lista~"
SHADOW_STARTUP_ANIM=true

# TTS
SHADOW_TTS_ENABLED=true
SHADOW_TTS_LANG="es-US"
SHADOW_TTS_RATE="1.1"
SHADOW_TTS_MSG="Onii-chan, tu terminal está lista~"

# Environment
export SHADOW_RICE="kawaii"
export PROMPT_EOL_MARK="~"
export BAT_THEME="Monokai Extended"

# Startup animation
if [[ "$SHADOW_STARTUP_ANIM" == "true" ]]; then
    mensaje="$SHADOW_STARTUP_MSG"
    color='\033[95m'
    fin_color='\033[0m'
    for ((i=0; i<${#mensaje}; i++)); do
        echo -ne "${color}${mensaje:$i:1}${fin_color}"
        sleep 0.12
    done
    echo
    sleep 0.3
fi

# TTS greeting
if [[ "$SHADOW_TTS_ENABLED" == "true" ]] && command -v termux-tts-speak &>/dev/null; then
    nohup sh -c "
        h=\$(date +%H)
        g='Buenas noches'
        [ \"\$h\" -ge 6 ] && [ \"\$h\" -lt 12 ] && g='Buenos días'
        [ \"\$h\" -ge 12 ] && [ \"\$h\" -lt 19 ] && g='Buenas tardes'
        termux-tts-speak -l ${SHADOW_TTS_LANG} -r ${SHADOW_TTS_RATE} \"\${g} onii-chan, tu terminal está lista\"
    " &>/dev/null &!
fi
