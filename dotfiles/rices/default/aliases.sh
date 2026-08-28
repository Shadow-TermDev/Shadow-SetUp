#!/data/data/com.termux/files/usr/bin/bash
# ================================================
#  Default RICE · Aliases
#  Ocean theme aliases
# ================================================

# -----------------------------------------------
# zoxide
# -----------------------------------------------
if command -v zoxide &>/dev/null; then
    eval "$(zoxide init zsh)"
    alias cd="z"
fi

# -----------------------------------------------
# ls → eza
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
# cat → bat
# -----------------------------------------------
if command -v bat &>/dev/null; then
    alias cat='bat --paging=never -pp'
    alias catp='bat'
fi

# -----------------------------------------------
# Sistema
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
# Seguridad
# -----------------------------------------------
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# -----------------------------------------------
# Git
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
# Python
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
# Quick edit
# -----------------------------------------------
alias zshrc='nano ~/.zshrc'
alias nanorc='nano ~/.nanorc'
alias reload='source ~/.zshrc'

# -----------------------------------------------
# Proot
# -----------------------------------------------
alias proot-start='proot-distro login ubuntu'

# -----------------------------------------------
# Shadow-SetUp
# -----------------------------------------------
alias sw='~/.local/bin/sw'
alias shadow='~/.local/bin/sw'
alias ss-update='sw update-core'
alias ss-status='sw status'
