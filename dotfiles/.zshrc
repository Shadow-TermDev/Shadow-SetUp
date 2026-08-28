# ================================================
#  Shadow-SetUp · .zshrc
#  Shell config con sistema modular
# ================================================

# -----------------------------------------------
# Esencial
# -----------------------------------------------
export ZSH_DISABLE_COMPFIX=true
export HISTFILE=/data/data/com.termux/files/home/.zsh_history
export HISTSIZE=75000
export SAVEHIST=75000
export EDITOR='nano'
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/bin:$PATH"

setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE
setopt HIST_REDUCE_BLANKS
setopt SHARE_HISTORY
setopt APPEND_HISTORY
setopt INC_APPEND_HISTORY
setopt HIST_VERIFY
setopt NO_BEEP

# -----------------------------------------------
# Oh My Zsh
# -----------------------------------------------
ZSH_THEME="powerlevel10k/powerlevel10k"
export ZSH="/data/data/com.termux/files/home/.oh-my-zsh"
plugins=(git zsh-autosuggestions zsh-syntax-highlighting fzf python)
source $ZSH/oh-my-zsh.sh

# Powerlevel10k config
[[ -f /data/data/com.termux/files/home/.p10k.zsh ]] && source /data/data/com.termux/files/home/.p10k.zsh

# -----------------------------------------------
# Autocompletado
# -----------------------------------------------
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=242'
ZSH_AUTOSUGGEST_STRATEGY=(history)
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=20
ZSH_AUTOSUGGEST_IGNORE_WIDGETS='expand-or-complete:*'

zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path "$XDG_CACHE_HOME/zsh/compcache"
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"

# -----------------------------------------------
# Animación de inicio
# -----------------------------------------------
mensaje="Iniciando terminal..."
color='\033[92m'
fin_color='\033[0m'
for ((i=0; i<${#mensaje}; i++)); do
    echo -ne "${color}${mensaje:$i:1}${fin_color}"
    sleep 0.15
done
echo
sleep 0.5

# -----------------------------------------------
# Environment
# -----------------------------------------------
export RISH_APPLICATION_ID='com.termux'
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export MANPAGER="sh -c 'col -bx | bat -l man -p'"
export BAT_THEME="ansi"

# -----------------------------------------------
# TTS: saludo kawaii
# -----------------------------------------------
if command -v termux-tts-speak &>/dev/null; then
    nohup sh -c '
        h=$(date +%H)
        g="Buenas noches"
        [ "$h" -ge 6 ] && [ "$h" -lt 12 ] && g="Buenos días"
        [ "$h" -ge 12 ] && [ "$h" -lt 19 ] && g="Buenas tardes"
        termux-tts-speak -l es-US -r 1.1 "${g} de nuevo Onii-chan... Tu terminal está lista, ¿vamos a programar?"
    ' &>/dev/null &!
fi

# -----------------------------------------------
# Aliases modulares
#  Se cargan desde ~/.shadow-setup/dotfiles/aliases.sh
# -----------------------------------------------
SHADOW_ALIASES="$HOME/.shadow-setup/dotfiles/aliases.sh"
[ -f "$SHADOW_ALIASES" ] && source "$SHADOW_ALIASES"

# -----------------------------------------------
# RICE activo
#  Se carga desde ~/.shadow-setup/active_rice.sh
# -----------------------------------------------
SHADOW_RICE="$HOME/.shadow-setup/active_rice.sh"
[ -f "$SHADOW_RICE" ] && source "$SHADOW_RICE"

# -----------------------------------------------
# Hardware/Seguridad
# -----------------------------------------------
umask 077
bindkey "^H" backward-kill-word

# -----------------------------------------------
# FZF
# -----------------------------------------------
if command -v fzf &>/dev/null; then
    bindkey '^R' fzf-history-widget
    bindkey '^[c' fzf-cd-widget

    export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git 2>/dev/null || find . -type f 2>/dev/null'
    export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
    export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git 2>/dev/null || find . -type d 2>/dev/null'

    if command -v bat &>/dev/null; then
        export FZF_DEFAULT_OPTS="--height 50% --layout=reverse --border --preview 'bat --color=always --style=numbers --line-range=:200 {} 2>/dev/null'"
    else
        export FZF_DEFAULT_OPTS='--height 50% --layout=reverse --border --preview "head -100 {} 2>/dev/null"'
    fi
fi
