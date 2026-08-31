#!/data/data/com.termux/files/usr/bin/bash
# ================================================
#  Term-Shadow RICE · Functions
#  Base functions (mkcd, extract, etc.) are loaded
#  automatically from aliases.sh.
#  Add rice-specific functions below.
# ================================================

# -----------------------------------------------
# Git helpers (names don't conflict with OMZ aliases)
# -----------------------------------------------
gtcom() { git commit -m "$1"; }
gtcof() { git checkout "$1" 2>/dev/null || git checkout -b "$1"; }
gtlog() { git log --oneline --graph --decorate -${1:-20}; }

# -----------------------------------------------
# Quick shortcuts
# -----------------------------------------------
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."
