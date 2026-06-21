#!/data/data/com.termux/files/usr/bin/bash
# =====================================================
#  Termux Setup Script
#  Instala y configura zsh + oh-my-zsh + plugins
# =====================================================

set -euo pipefail

# -----------------------------------------------
# Colores
# -----------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;92m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[✓]${NC} $1"; }
info() { echo -e "${CYAN}[→]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
fail() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# -----------------------------------------------
# Banner
# -----------------------------------------------
clear
echo -e "${CYAN}${BOLD}"
echo -e "  ╔══════════════════════════════════╗"
echo -e "  ║       🖤  Shadow-SetUp  🖤       ║"
echo -e "  ╚══════════════════════════════════╝"
echo -e "${NC}"
echo -e "  ${BOLD}zsh · Oh My Zsh · Powerlevel10k${NC}"
echo -e "  ${BOLD}Plugins · Fuentes · Dotfiles${NC}"
echo ""

# -----------------------------------------------
# 1. Borrar motd (mensaje de bienvenida por defecto)
# -----------------------------------------------
MOTD="/data/data/com.termux/files/usr/etc/motd"
if [ -f "$MOTD" ]; then
    rm -f "$MOTD"
    ok "motd eliminado"
else
    warn "motd no encontrado, omitiendo..."
fi

# -----------------------------------------------
# 2. Actualizar repositorios
# -----------------------------------------------
info "Actualizando repositorios..."
pkg update -y &>/dev/null && pkg upgrade -y &>/dev/null
ok "Repositorios actualizados"

# -----------------------------------------------
# 3. Instalar paquetes esenciales
# -----------------------------------------------
info "Instalando paquetes esenciales..."
PKGS=(
    zsh git curl wget nano bat eza fd fzf zoxide
    python python-pip nodejs-lts
    termux-api openssh man
)

for pkg in "${PKGS[@]}"; do
    if pkg list-installed 2>/dev/null | grep -q "^$pkg/"; then
        warn "$pkg ya instalado, omitiendo..."
    else
        info "Instalando $pkg..."
        pkg install -y "$pkg" &>/dev/null || warn "No se pudo instalar $pkg, continuando..."
        ok "$pkg instalado"
    fi
done

# -----------------------------------------------
# 4. Instalar Oh My Zsh
# -----------------------------------------------
if [ -d "$HOME/.oh-my-zsh" ]; then
    warn "Oh My Zsh ya existe, omitiendo instalación..."
else
    info "Instalando Oh My Zsh..."
    RUNZSH=no CHSH=no sh -c \
        "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" \
        &>/dev/null || fail "Error instalando Oh My Zsh"
    ok "Oh My Zsh instalado"
fi

ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"

# -----------------------------------------------
# 5. Instalar Powerlevel10k
# -----------------------------------------------
P10K_DIR="$ZSH_CUSTOM/themes/powerlevel10k"
if [ -d "$P10K_DIR" ]; then
    warn "Powerlevel10k ya existe, actualizando..."
    git -C "$P10K_DIR" pull --quiet &>/dev/null
else
    info "Instalando Powerlevel10k..."
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$P10K_DIR" \
        &>/dev/null || fail "Error clonando Powerlevel10k"
    ok "Powerlevel10k instalado"
fi

# -----------------------------------------------
# 6. Instalar plugins de zsh
# -----------------------------------------------
install_plugin() {
    local name="$1"
    local repo="$2"
    local dir="$ZSH_CUSTOM/plugins/$name"
    if [ -d "$dir" ]; then
        warn "Plugin $name ya existe, actualizando..."
        git -C "$dir" pull --quiet &>/dev/null
    else
        info "Instalando plugin: $name..."
        git clone --depth=1 "$repo" "$dir" \
            &>/dev/null || warn "No se pudo instalar $name"
        ok "Plugin $name instalado"
    fi
}

install_plugin "zsh-autosuggestions" \
    "https://github.com/zsh-users/zsh-autosuggestions"

install_plugin "zsh-syntax-highlighting" \
    "https://github.com/zsh-users/zsh-syntax-highlighting"

# -----------------------------------------------
# 6. Escribir .zshrc
# -----------------------------------------------
info "Escribiendo ~/.zshrc..."

# Hacer backup si ya existe
if [ -f "$HOME/.zshrc" ]; then
    BACKUP="$HOME/.zshrc.bak.$(date +%Y%m%d%H%M%S)"
    cp "$HOME/.zshrc" "$BACKUP"
    warn "Backup guardado en $BACKUP"
fi

cat > "$HOME/.zshrc" << 'ZSHRC'
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

zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path "$XDG_CACHE_HOME/zsh/compcache"
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=' 'l:| r:|='
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
opencode() {
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

search()    { find . -type f -name "$1" 2>/dev/null; }
biggest()   { du -sh * 2>/dev/null | sort -rh | head -${1:-10}; }
bak()       { cp "$1"{,.bak.$(date +%Y%m%d%H%M%S)}; }
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
ZSHRC

ok ".zshrc escrito correctamente"

# -----------------------------------------------
# 7. Descargar .p10k.zsh desde el repo
# -----------------------------------------------
REPO_RAW="https://raw.githubusercontent.com/Shadow-TermDev/Shadow-SetUp/main"

info "Descargando .p10k.zsh..."
if curl -fsSL "$REPO_RAW/dotfiles/.p10k.zsh" -o "$HOME/.p10k.zsh"; then
    ok ".p10k.zsh descargado"
else
    warn "No se pudo descargar .p10k.zsh — se configurará al iniciar zsh"
fi

# -----------------------------------------------
# 8. Copiar dotfiles de .termux
# -----------------------------------------------
info "Configurando ~/.termux..."
mkdir -p "$HOME/.termux"

for f in colors.properties termux.properties; do
    if curl -fsSL "$REPO_RAW/dotfiles/.termux/$f" -o "$HOME/.termux/$f"; then
        ok "$f copiado"
    else
        warn "No se pudo descargar $f"
    fi
done

# Recargar configuración de Termux si está disponible
if command -v termux-reload-settings &>/dev/null; then
    termux-reload-settings
    ok "Configuración de Termux recargada"
fi

# -----------------------------------------------
# 9. Instalar fuente MesloLGS NF (para Powerlevel10k)
# -----------------------------------------------
FONT_PATH="$HOME/.termux/font.ttf"
FONT_URL="https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Regular.ttf"

if [ -f "$FONT_PATH" ]; then
    warn "font.ttf ya existe, omitiendo..."
else
    info "Descargando MesloLGS NF..."
    if curl -fsSL "$FONT_URL" -o "$FONT_PATH"; then
        ok "Fuente MesloLGS NF instalada en ~/.termux/font.ttf"
    else
        warn "No se pudo descargar la fuente — instálala manualmente desde:"
        warn "https://github.com/romkatv/powerlevel10k#meslo-nerd-font-patched-for-powerlevel10k"
    fi
fi

# -----------------------------------------------
# 10. Cambiar shell a zsh
# -----------------------------------------------
info "Configurando zsh como shell predeterminado..."
if [ "$SHELL" != "$(which zsh)" ]; then
    chsh -s zsh 2>/dev/null || warn "No se pudo cambiar shell automáticamente. Ejecuta: chsh -s zsh"
else
    ok "zsh ya es el shell predeterminado"
fi

# -----------------------------------------------
# 11. Resumen final
# -----------------------------------------------
clear
echo -e "${CYAN}${BOLD}"
echo -e "  ╔══════════════════════════════════╗"
echo -e "  ║       🖤  Shadow-SetUp  🖤       ║"
echo -e "  ╚══════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${GREEN}${BOLD}══════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  ✓ Setup completado exitosamente!${NC}"
echo -e "${GREEN}${BOLD}══════════════════════════════════════${NC}"
echo ""
echo -e "  ${BOLD}Próximos pasos:${NC}"
echo -e "  ${CYAN}1.${NC} Reinicia Termux o ejecuta: ${BOLD}exec zsh${NC}"
echo -e "  ${CYAN}2.${NC} El tema Powerlevel10k cargará automáticamente"
echo -e "  ${CYAN}3.${NC} Si algo falla: ${BOLD}p10k configure${NC}"
echo -e "  ${CYAN}4.${NC} Si usas proot/Ubuntu, instala opencode manualmente"
echo ""
echo -e "  ${YELLOW}Recuerda:${NC} Actualiza la variable REPO_RAW con tu usuario de GitHub"
echo ""
