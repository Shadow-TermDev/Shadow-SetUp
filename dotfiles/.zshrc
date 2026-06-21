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
setopt GLOB_DOTS
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
ZSH_AUTOSUGGEST_STRATEGY=(history completion)

zstyle ':completion:' use-cache on
zstyle ':completion:' cache-path "$XDG_CACHE_HOME/zsh/compcache"
zstyle ':completion:' menu select
zstyle ':completion:' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=' 'l:| r:|='
zstyle ':completion:' list-colors "${(s.:.)LS_COLORS}"

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
# zoxide
# -----------------------------------------------
if command -v zoxide &>/dev/null; then
    eval "$(zoxide init zsh)"
    alias cd="z"
fi

# -----------------------------------------------
# Aliases: ls → eza
# -----------------------------------------------
if command -v eza &>/dev/null; then
    alias ls='eza --icons --group-directories-first --time-style=long-iso'
    alias ll='eza -lah --icons --group-directories-first'
    alias la='eza -a --icons --group-directories-first'
    alias l='eza -lh --icons --group-directories-first'
    alias lt='eza -T --icons --group-directories-first'
else
    alias ll='ls -lah'
    alias la='ls -a'
    alias l='ls -lh'
fi

# -----------------------------------------------
# Aliases: cat → bat
# -----------------------------------------------
if command -v bat &>/dev/null; then
    alias cat='bat --paging=never -pp'
    alias catp='bat'
fi

# -----------------------------------------------
# Aliases: Sistema
# -----------------------------------------------
alias update='pkg update && pkg upgrade'
alias clean='pkg clean'
alias myip='curl -s ifconfig.me'
alias c='clear'
alias cls='clear'
alias h='history'
alias hg='history | grep'
alias x='exit'
alias ports='ss -tulanp'
alias localip='ip -brief addr'
alias mkdir='mkdir -pv'

# -----------------------------------------------
# Aliases: Seguridad
# -----------------------------------------------
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# -----------------------------------------------
# Aliases: Git
# -----------------------------------------------
alias gs='git status'
alias ga='git add'
alias gaa='git add --all'
alias gc='git commit -m'
alias gca='git commit -am'
alias gp='git push'
alias gpl='git pull'
alias gpr='git pull --rebase'
alias gl='git log --oneline --graph --decorate -20'
alias gd='git diff'
alias gds='git diff --staged'
alias gco='git checkout'
alias gcb='git checkout -b'
alias gb='git branch'
alias gm='git merge'
alias gr='git remote'
alias gst='git stash'
alias gstp='git stash pop'

# -----------------------------------------------
# Aliases: Python
# -----------------------------------------------
alias py='python3'
alias python='python3'
alias pip='pip3'
alias venv='python3 -m venv'
alias activate='source venv/bin/activate'
alias pipup='pip install --upgrade pip'
alias pipreq='pip install -r requirements.txt'
alias pyserver='python3 -m http.server 8000'

# -----------------------------------------------
# Aliases: Quick edit
# -----------------------------------------------
alias zshrc='nano ~/.zshrc'
alias reload='source ~/.zshrc'

# -----------------------------------------------
# Aliases: Proot
# -----------------------------------------------
alias proot-start='proot-distro login ubuntu'
# Ejecutar OpenCode de Proot-Distro desde Termux Nativo
opencode() {
    # 'proot-distro login' acepta pasarle un comando directo a ejecutar en su entorno
    proot-distro login ubuntu --shared-tmp --bind "$PWD:/workspace" -- sh -c "cd /workspace && /root/.opencode/bin/opencode $*"
}


# -----------------------------------------------
# Funciones
# -----------------------------------------------
mkcd() { mkdir -p "$1" && cd "$1"; }

extract() {
    if [ -f "$1" ]; then
        case "$1" in
            *.tar.bz2)   tar xjf "$1"   ;;
            *.tar.gz)    tar xzf "$1"   ;;
            *.tar.xz)    tar xJf "$1"   ;;
            *.bz2)       bunzip2 "$1"   ;;
            *.rar)       unrar x "$1"   ;;
            *.gz)        gunzip "$1"    ;;
            *.tar)       tar xf "$1"    ;;
            *.tbz2)      tar xjf "$1"   ;;
            *.tgz)       tar xzf "$1"   ;;
            *.zip)       unzip "$1"     ;;
            *.7z)        7z x "$1"      ;;
            *.zst)       unzstd "$1"    ;;
            *)           echo "'$1' no se puede extraer" ;;
        esac
    else
        echo "'$1' no es un archivo válido"
    fi
}

search() { find . -type f -name "$1" 2>/dev/null; }
biggest() { du -sh * 2>/dev/null | sort -rh | head -${1:-10}; }
bak() { cp "$1"{,.bak.$(date +%Y%m%d%H%M%S)}; }
portcheck() { ss -tulanp 2>/dev/null | grep ":$1 " || echo "Puerto $1 libre"; }

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
