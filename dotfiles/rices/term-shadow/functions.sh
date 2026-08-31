#!/data/data/com.termux/files/usr/bin/bash
# ================================================
#  Term-Shadow RICE · Functions
#  Personal theme functions
# ================================================

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
            *)           echo "'$1' cannot be extracted" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

search()    { find . -type f -name "$1" 2>/dev/null; }
biggest()   { du -sh * 2>/dev/null | sort -rh | head -${1:-10}; }
bak()       { cp "$1"{,.bak.$(date +%Y%m%d%H%M%S)}; }
portcheck() { ss -tulanp 2>/dev/null | grep ":$1 " || echo "Port $1 is free"; }

# -----------------------------------------------
# Git helpers (names don't conflict with OMZ aliases)
# -----------------------------------------------
gcom() { git commit -m "$1"; }
gcof() { git checkout "$1" 2>/dev/null || git checkout -b "$1"; }
glgg() { git log --oneline --graph --decorate -${1:-20}; }

# -----------------------------------------------
# Quick shortcuts
# -----------------------------------------------
..()   { cd ..; }
...()  { cd ../..; }
....() { cd ../../..; }
