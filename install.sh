#!/usr/bin/env bash
# ================================================
#  Shadow-SetUp · Installer
#  Usage: curl -fsSL <url>/install.sh | bash
# ================================================

set -uo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;92m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
info() { echo -e "${CYAN}[>>]${NC} $1"; }
warn() { echo -e "${YELLOW}[!!]${NC} $1"; }
fail() { echo -e "${RED}[XX]${NC} $1"; exit 1; }

trap 'echo -e "\n${YELLOW}[!!]${NC} Cancelled"; exit 1' INT

# -----------------------------------------------
# Banner
# -----------------------------------------------
clear
echo -e "${CYAN}${BOLD}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║             Shadow-SetUp              ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${NC}"
echo -e "  ${BOLD}Modular Termux Environment Manager${NC}"
echo -e "  ${DIM}https://Shadow-TermDev.github.io${NC}"
echo ""

# -----------------------------------------------
# Paths
# -----------------------------------------------
SHADOW_DATA="$HOME/.shadow-setup"
SHADOW_BIN="$HOME/.local/bin"

# -----------------------------------------------
# Dependencies
# -----------------------------------------------
info "Checking dependencies..."

command -v python3 &>/dev/null || { warn "Installing python..."; pkg install -y python &>/dev/null || fail "Python install failed"; }
command -v git &>/dev/null || { warn "Installing git..."; pkg install -y git &>/dev/null || fail "Git install failed"; }
command -v curl &>/dev/null || { warn "Installing curl..."; pkg install -y curl &>/dev/null || fail "curl install failed"; }

ok "Dependencies ready"

# -----------------------------------------------
# Python packages
# -----------------------------------------------
info "Installing Python packages..."
pip install --user rich colorama InquirerPy pyfiglet &>/dev/null || warn "pip install partial fail"
ok "Python packages installed"

# -----------------------------------------------
# Directories
# -----------------------------------------------
info "Setting up directories..."
mkdir -p "$SHADOW_DATA" "$SHADOW_DATA/cache" "$SHADOW_DATA/backups" "$SHADOW_BIN"
ok "Directories ready"

# -----------------------------------------------
# Clone repo
# -----------------------------------------------
TEMP_DIR="$SHADOW_DATA/cache/shadow-install"
rm -rf "$TEMP_DIR"

info "Downloading Shadow-SetUp..."
git clone --depth=1 https://github.com/Shadow-TermDev/Shadow-SetUp.git "$TEMP_DIR" &>/dev/null \
    || fail "Failed to download repository"
ok "Repository downloaded"

# -----------------------------------------------
# Install files (EXCEPT rices — handled later)
# -----------------------------------------------
info "Installing files..."

[ -d "$TEMP_DIR/_lib" ] && { rm -rf "$SHADOW_DATA/_lib"; cp -r "$TEMP_DIR/_lib" "$SHADOW_DATA/_lib"; ok "_lib installed"; }

if [ -d "$TEMP_DIR/dotfiles" ]; then
    rm -rf "$SHADOW_DATA/dotfiles"
    mkdir -p "$SHADOW_DATA/dotfiles"
    # Copy everything EXCEPT rices directory
    for item in "$TEMP_DIR/dotfiles"/*; do
        item_name=$(basename "$item")
        [ "$item_name" = "rices" ] && continue
        cp -r "$item" "$SHADOW_DATA/dotfiles/"
    done
    ok "dotfiles installed"
fi

[ -f "$TEMP_DIR/.version" ] && { cp "$TEMP_DIR/.version" "$SHADOW_DATA/.version"; ok ".version installed"; }

# -----------------------------------------------
# CLI wrappers
# -----------------------------------------------
info "Creating CLI commands..."
for cmd in sw shadow; do
    cat > "$SHADOW_BIN/$cmd" << EOF
#!/data/data/com.termux/files/usr/bin/bash
exec python3 "$SHADOW_DATA/_lib/cli.py" "\$@"
EOF
    chmod +x "$SHADOW_BIN/$cmd"
    ok "Command '$cmd' created"
done

# -----------------------------------------------
# PATH
# -----------------------------------------------
info "Setting up PATH..."
SHELL_RC="$HOME/.zshrc"
[ ! -f "$SHELL_RC" ] && SHELL_RC="$HOME/.bashrc"
if ! grep -q '\.local/bin' "$SHELL_RC" 2>/dev/null; then
    echo '' >> "$SHELL_RC"
    echo '# Shadow-SetUp PATH' >> "$SHELL_RC"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    ok "PATH added"
else
    ok "PATH already configured"
fi

# -----------------------------------------------
# Module installation
# -----------------------------------------------
echo ""
echo -e "${BOLD}What would you like to install?${NC}"
echo ""
echo "  [1] Full setup (all modules)"
echo "  [2] Minimal (shell + tools only)"
echo "  [3] Skip (configure later)"
echo ""
read -p "  Choice [1]: " choice < /dev/tty
choice="${choice:-1}"

case "$choice" in
    1) python3 "$SHADOW_DATA/_lib/cli.py" install shell tools dotfiles aliases < /dev/tty ;;
    2) python3 "$SHADOW_DATA/_lib/cli.py" install shell tools < /dev/tty ;;
    3) info "Skipping module install" ;;
    *) python3 "$SHADOW_DATA/_lib/cli.py" install shell tools dotfiles aliases < /dev/tty ;;
esac

# -----------------------------------------------
# RICE selection — ONLY COPY SELECTED ONE
# -----------------------------------------------
echo ""
echo -e "${BOLD}--- RICE Selection ---${NC}"
echo ""

# RICEs from downloaded repo
REPO_RICES="$TEMP_DIR/dotfiles/rices"
RICE_LIST=()

if [ -d "$REPO_RICES" ]; then
    # Use find instead of glob for reliability
    while IFS= read -r d; do
        [ -f "$d/rice.sh" ] && RICE_LIST+=("$(basename "$d")")
    done < <(find "$REPO_RICES" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort)
fi

RICE_COUNT=${#RICE_LIST[@]}

if [ "$RICE_COUNT" -eq 0 ]; then
    info "No RICEs available"
else
    for i in "${!RICE_LIST[@]}"; do
        echo "  [$((i+1))] ${RICE_LIST[$i]}"
    done
    echo "  [s] Skip"
    echo ""
    read -p "  Choice [1]: " rice_input < /dev/tty
    rice_input="${rice_input:-1}"

    if [ "$rice_input" = "s" ] || [ "$rice_input" = "S" ]; then
        info "No RICE selected"
    elif [ "$rice_input" -ge 1 ] && [ "$rice_input" -le "$RICE_COUNT" ] 2>/dev/null; then
        PICKED="${RICE_LIST[$((rice_input-1))]}"
        # Copy ONLY this RICE
        mkdir -p "$SHADOW_DATA/dotfiles/rices"
        cp -r "$REPO_RICES/$PICKED" "$SHADOW_DATA/dotfiles/rices/"
        info "Installing '$PICKED'..."
        python3 "$SHADOW_DATA/_lib/cli.py" rice set "$PICKED" < /dev/tty
    else
        warn "Invalid choice, skipping..."
    fi
fi

# -----------------------------------------------
# Clean up temp
# -----------------------------------------------
rm -rf "$TEMP_DIR"

# -----------------------------------------------
# Final
# -----------------------------------------------
echo ""
echo -e "${GREEN}${BOLD}Installation complete!${NC}"
echo ""
echo -e "  Run: ${BOLD}sw${NC}           # Interactive menu"
echo -e "  Or: ${BOLD}sw help${NC}       # Show commands"
echo ""
echo -e "  ${DIM}Shadow-TermDev · https://Shadow-TermDev.github.io${NC}"
echo ""
