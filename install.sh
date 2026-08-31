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
# Python packages (basic, before clone)
# -----------------------------------------------
info "Installing Python packages..."
pip install --user rich InquirerPy pyfiglet &>/dev/null || warn "pip install partial fail"
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
    # Preserve existing rices before overwriting
    EXISTING_RICES=""
    if [ -d "$SHADOW_DATA/dotfiles/rices" ]; then
        EXISTING_RICES="$SHADOW_DATA/cache/existing_rices_backup"
        rm -rf "$EXISTING_RICES"
        cp -r "$SHADOW_DATA/dotfiles/rices" "$EXISTING_RICES"
    fi
    
    rm -rf "$SHADOW_DATA/dotfiles"
    mkdir -p "$SHADOW_DATA/dotfiles"
    # Copy everything EXCEPT rices directory
    for item in "$TEMP_DIR/dotfiles"/*; do
        item_name=$(basename "$item")
        [ "$item_name" = "rices" ] && continue
        cp -r "$item" "$SHADOW_DATA/dotfiles/"
    done
    # Restore existing rices (if any)
    if [ -n "$EXISTING_RICES" ] && [ -d "$EXISTING_RICES" ]; then
        mkdir -p "$SHADOW_DATA/dotfiles/rices"
        for item in "$EXISTING_RICES"/*; do
            item_name=$(basename "$item")
            [ "$item_name" = "manifest.json" ] && continue
            cp -r "$item" "$SHADOW_DATA/dotfiles/rices/"
        done
        rm -rf "$EXISTING_RICES"
    fi
    # Copy manifest.json for RICE detection
    [ -f "$TEMP_DIR/dotfiles/rices/manifest.json" ] && {
        mkdir -p "$SHADOW_DATA/dotfiles/rices"
        cp "$TEMP_DIR/dotfiles/rices/manifest.json" "$SHADOW_DATA/dotfiles/rices/"
    }
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
# Helper: install default RICE if no local RICEs exist
install_default_if_needed() {
    LOCAL_RICES="$SHADOW_DATA/dotfiles/rices"
    HAS_RICES=false
    if [ -d "$LOCAL_RICES" ]; then
        for d in "$LOCAL_RICES"/*; do
            [ -d "$d" ] && [ -f "$d/rice.sh" ] && HAS_RICES=true && break
        done
    fi
    
    if [ "$HAS_RICES" = false ]; then
        if [ -d "$REPO_RICES/default" ]; then
            mkdir -p "$SHADOW_DATA/dotfiles/rices"
            cp -r "$REPO_RICES/default" "$SHADOW_DATA/dotfiles/rices/"
            info "No RICEs found — installing default..."
            python3 "$SHADOW_DATA/_lib/cli.py" rice set default < /dev/tty
        fi
    else
        info "RICEs exist — keeping current setup"
    fi
}

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
        # Skip: install default only if no RICEs exist
        install_default_if_needed
    elif [[ "$rice_input" =~ ^[0-9]+$ ]] && [ "$rice_input" -ge 1 ] && [ "$rice_input" -le "$RICE_COUNT" ]; then
        PICKED="${RICE_LIST[$((rice_input-1))]}"
        # Copy ONLY this RICE
        mkdir -p "$SHADOW_DATA/dotfiles/rices"
        cp -r "$REPO_RICES/$PICKED" "$SHADOW_DATA/dotfiles/rices/"
        info "Installing '$PICKED'..."
        python3 "$SHADOW_DATA/_lib/cli.py" rice set "$PICKED" < /dev/tty
    else
        # Invalid: install default only if no RICEs exist
        warn "Invalid choice, using default..."
        install_default_if_needed
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
