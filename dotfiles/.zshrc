# ================================================
#  Shadow-SetUp · .zshrc
#  Minimal — RICE handles everything
# ================================================

# -----------------------------------------------
# Core
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
# RICE early check — read SHADOW_DISABLE_P10K without sourcing (avoids double anim)
# -----------------------------------------------
if [[ -f "$HOME/.shadow-setup/active_rice.sh" ]]; then
    if grep -q 'SHADOW_DISABLE_P10K="true"' "$HOME/.shadow-setup/active_rice.sh" 2>/dev/null; then
        SHADOW_DISABLE_P10K="true"
    fi
fi

# -----------------------------------------------
# Oh My Zsh
# -----------------------------------------------
if [[ "$SHADOW_DISABLE_P10K" == "true" ]]; then
    ZSH_THEME=""
else
    ZSH_THEME="powerlevel10k/powerlevel10k"
fi
export ZSH="/data/data/com.termux/files/home/.oh-my-zsh"

# Suppress p10k wizard when no config exists (e.g. custom-prompt rices)
[[ ! -f ~/.p10k.zsh ]] && typeset -g POWERLEVEL9K_DISABLE_CONFIGURATION_WIZARD=true

# Auto-detect installed plugins
_zsh_plugins=()
for _p in zsh-autosuggestions zsh-syntax-highlighting fzf python; do
    [[ -d "$ZSH/custom/plugins/$_p" ]] && _zsh_plugins+=("$_p")
done
plugins=(git "${_zsh_plugins[@]}")
unset _p _zsh_plugins

source $ZSH/oh-my-zsh.sh

# Powerlevel10k config (only if not disabled)
if [[ "$SHADOW_DISABLE_P10K" != "true" ]]; then
    [[ -f ~/.p10k.zsh ]] && source ~/.p10k.zsh
fi

# -----------------------------------------------
# Autocomplete — Global, agnóstico, pipe-aware
#  Soporta tuberías (|), subcomandos y pipes encadenados
#  sin depender de ningún RICE (100% agnóstico)
# -----------------------------------------------
# XDG fallback para Termux minimal
[[ -z "${XDG_CACHE_HOME:-}" ]] && export XDG_CACHE_HOME="$HOME/.cache"
[[ -d "$XDG_CACHE_HOME/zsh/compcache" ]] || mkdir -p "$XDG_CACHE_HOME/zsh/compcache"

ZSH_AUTOSUGGEST_STRATEGY=(history completion)
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=#4c566a'
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=30
ZSH_AUTOSUGGEST_USE_ASYNC=true
ZSH_AUTOSUGGEST_MANUAL_REBIND=1
ZSH_AUTOSUGGEST_IGNORE_WIDGETS='expand-or-complete:*'

zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path "$XDG_CACHE_HOME/zsh/compcache"
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' rehash true
zstyle ':completion:*' completer _complete _ignored _approximate
zstyle ':completion:*' verbose true
zstyle ':completion:*' squeeze-slashes true
zstyle ':completion:*' accept-exact '*(N)'
zstyle ':completion::complete:*' gain-privileges 1

setopt ALWAYS_TO_END
setopt AUTO_MENU
setopt COMPLETE_IN_WORD
setopt AUTO_LIST
setopt AUTO_PARAM_SLASH
setopt EXTENDED_GLOB

# -----------------------------------------------
# Environment
# -----------------------------------------------
export RISH_APPLICATION_ID='com.termux'
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export MANPAGER="sh -c 'col -bx | bat -l man -p'"

# -----------------------------------------------
# Security
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

# -----------------------------------------------
# RICE activo (aliases, functions, animation, TTS)
# -----------------------------------------------
SHADOW_RICE="$HOME/.shadow-setup/active_rice.sh"
[ -f "$SHADOW_RICE" ] && source "$SHADOW_RICE"

# Base aliases (always loaded — includes functions like mkcd, extract)
SHADOW_BASE_ALIASES="$HOME/.shadow-setup/dotfiles/aliases.sh"
[ -f "$SHADOW_BASE_ALIASES" ] && source "$SHADOW_BASE_ALIASES"

# RICE aliases (overrides/extends base if present)
SHADOW_ALIASES="$HOME/.shadow-setup/aliases.sh"
[ -f "$SHADOW_ALIASES" ] && source "$SHADOW_ALIASES"

# RICE functions
SHADOW_FUNCTIONS="$HOME/.shadow-setup/functions.sh"
[ -f "$SHADOW_FUNCTIONS" ] && source "$SHADOW_FUNCTIONS"
