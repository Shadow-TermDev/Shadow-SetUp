#!/data/data/com.termux/files/usr/bin/bash
# ================================================
#  Shadow-SetUp · Aliases y funciones
#  Fuente: source ~/.shadow-aliases
# ================================================

# -----------------------------------------------
# zoxide — shell-agnóstico (zsh / bash)
#  Modular: inicializa el shell correcto, evita duplicar lógica en RICEs
# -----------------------------------------------
if command -v zoxide &>/dev/null; then
    if [[ -n "${ZSH_VERSION:-}" ]]; then
        eval "$(zoxide init zsh)"
    elif [[ -n "${BASH_VERSION:-}" ]]; then
        eval "$(zoxide init bash)"
    fi
    alias cd="z"
    alias cdi="zi" 2>/dev/null || true
fi

# -----------------------------------------------
# Aliases: ls → eza (Nerd Fonts aware)
#  --icons=auto: muestra iconos solo si la font los soporta (evita □)
#  --color=auto: respeta pipes y NO_COLOR
#  Funciones aseguran que `eza` sin args liste "." (fix eza 0.23.5)
# -----------------------------------------------
if command -v eza &>/dev/null; then
    ls() { if [ $# -eq 0 ]; then eza --icons=auto --group-directories-first --color=auto --time-style=long-iso .; else eza --icons=auto --group-directories-first --color=auto --time-style=long-iso "$@"; fi; }
    ll() { if [ $# -eq 0 ]; then eza -lah --icons=auto --group-directories-first --git --color=auto .; else eza -lah --icons=auto --group-directories-first --git --color=auto "$@"; fi; }
    la() { if [ $# -eq 0 ]; then eza -a --icons=auto --group-directories-first --color=auto .; else eza -a --icons=auto --group-directories-first --color=auto "$@"; fi; }
    l() { if [ $# -eq 0 ]; then eza -lh --icons=auto --group-directories-first --color=auto .; else eza -lh --icons=auto --group-directories-first --color=auto "$@"; fi; }
    lt() { eza -T --icons=auto --group-directories-first --level=2 --color=auto "${@:-.}"; }
    lta() { eza -Ta --icons=auto --group-directories-first --color=auto "${@:-.}"; }
else
    alias ls='ls --color=auto'
    alias ll='ls -lah --color=auto'
    alias la='ls -A --color=auto'
    alias l='ls -lh --color=auto'
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
alias nanorc='nano ~/.nanorc'
alias reload='source ~/.zshrc'

# -----------------------------------------------
# Aliases: Proot
# -----------------------------------------------
alias proot-start='proot-distro login ubuntu'

# -----------------------------------------------
# Aliases: Shadow-SetUp
# -----------------------------------------------
alias sw='~/.local/bin/sw'
alias shadow='~/.local/bin/sw'
alias ss-update='sw update-core'
alias ss-status='sw status'

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

search()    { find . -type f -name "$1" 2>/dev/null; }
biggest()   { du -sh * 2>/dev/null | sort -rh | head -${1:-10}; }
bak()       { cp "$1"{,.bak.$(date +%Y%m%d%H%M%S)}; }
portcheck() { ss -tulanp 2>/dev/null | grep ":$1 " || echo "Puerto $1 libre"; }
