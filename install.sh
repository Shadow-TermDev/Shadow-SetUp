#!/usr/bin/env bash
# ================================================
#  Shadow-SetUp · Installer
#  Usage: curl -fsSL <url>/install.sh | bash
# ================================================

set -euo pipefail

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

# -----------------------------------------------
# Banner
# -----------------------------------------------
clear
echo -e "${CYAN}${BOLD}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║           Shadow-SetUp v2             ║"
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
# Check dependencies
# -----------------------------------------------
info "Checking dependencies..."

if ! command -v python3 &>/dev/null; then
    warn "Python3 not found. Installing..."
    pkg install -y python &>/dev/null || fail "Failed to install Python"
fi

if ! command -v git &>/dev/null; then
    warn "Git not found. Installing..."
    pkg install -y git &>/dev/null || fail "Failed to install Git"
fi

if ! command -v curl &>/dev/null; then
    warn "curl not found. Installing..."
    pkg install -y curl &>/dev/null || fail "Failed to install curl"
fi

ok "Dependencies ready"

# -----------------------------------------------
# Install Python packages
# -----------------------------------------------
info "Installing Python packages..."

pip install --user rich colorama InquirerPy pyfiglet &>/dev/null || {
    warn "pip install failed, trying with pkg..."
    pkg install -y python-rich python-colorama &>/dev/null || warn "Some packages may not be available"
}

ok "Python packages installed"

# -----------------------------------------------
# Create directories
# -----------------------------------------------
info "Setting up directories..."

mkdir -p "$SHADOW_DATA"
mkdir -p "$SHADOW_DATA/cache"
mkdir -p "$SHADOW_DATA/backups"
mkdir -p "$SHADOW_BIN"

ok "Directories ready"

# -----------------------------------------------
# Clone repo
# -----------------------------------------------
TEMP_DIR="$SHADOW_DATA/cache/shadow-install"

if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

info "Downloading Shadow-SetUp..."
git clone --depth=1 https://github.com/Shadow-TermDev/Shadow-SetUp.git "$TEMP_DIR" &>/dev/null \
    || fail "Failed to download repository"

ok "Repository downloaded"

# -----------------------------------------------
# Install files
# -----------------------------------------------
info "Installing files..."

if [ -d "$TEMP_DIR/_lib" ]; then
    rm -rf "$SHADOW_DATA/_lib"
    cp -r "$TEMP_DIR/_lib" "$SHADOW_DATA/_lib"
    ok "_lib installed"
fi

if [ -d "$TEMP_DIR/dotfiles" ]; then
    rm -rf "$SHADOW_DATA/dotfiles"
    cp -r "$TEMP_DIR/dotfiles" "$SHADOW_DATA/dotfiles"
    ok "dotfiles installed"
fi

if [ -f "$TEMP_DIR/.version" ]; then
    cp "$TEMP_DIR/.version" "$SHADOW_DATA/.version"
    ok ".version installed"
fi

# -----------------------------------------------
# Create CLI wrappers
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
# PATH setup
# -----------------------------------------------
info "Setting up PATH..."

SHELL_RC="$HOME/.zshrc"
[ ! -f "$SHELL_RC" ] && SHELL_RC="$HOME/.bashrc"

if ! grep -q '\.local/bin' "$SHELL_RC" 2>/dev/null; then
    echo '' >> "$SHELL_RC"
    echo '# Shadow-SetUp PATH' >> "$SHELL_RC"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    ok "PATH added to $(basename $SHELL_RC)"
else
    warn "~/.local/bin already in PATH"
fi

# -----------------------------------------------
# Clean up
# -----------------------------------------------
rm -rf "$TEMP_DIR"

# -----------------------------------------------
# Module installation
# -----------------------------------------------
echo ""
echo -e "${BOLD}What would you like to install?${NC}"
echo ""
echo "  [1] Full setup (all modules)"
echo "  [2] Minimal (shell + tools only)"
echo "  [3] Custom (choose modules)"
echo "  [4] Skip (configure later)"
echo ""
read -p "  Choice [1]: " choice
choice="${choice:-1}"

case "$choice" in
    1)
        python3 "$SHADOW_DATA/_lib/cli.py" install shell tools dotfiles aliases
        ;;
    2)
        python3 "$SHADOW_DATA/_lib/cli.py" install shell tools
        ;;
    3)
        echo ""
        echo "Available modules: shell, tools, fonts, dotfiles, aliases"
        read -p "  Modules (space-separated): " modules
        python3 "$SHADOW_DATA/_lib/cli.py" install $modules
        ;;
    4)
        info "Skipping setup. Run 'sw install <module>' later."
        ;;
    *)
        warn "Invalid choice, running full setup..."
        python3 "$SHADOW_DATA/_lib/cli.py" install shell tools dotfiles aliases
        ;;
esac

# -----------------------------------------------
# RICE selection (only available RICEs)
# -----------------------------------------------
echo ""
echo -e "${BOLD}Select a RICE theme:${NC}"
echo ""

RICES_DIR="$SHADOW_DATA/dotfiles/rices"
RICE_OPTS=()
RICE_NUM=1

for rice_dir in "$RICES_DIR"/*/; do
    if [ -f "$rice_dir/rice.sh" ]; then
        rice_name=$(basename "$rice_dir")
        echo "  [$RICE_NUM] $rice_name"
        RICE_OPTS+=("$rice_name")
        RICE_NUM=$((RICE_NUM + 1))
    fi
done

echo "  [$RICE_NUM] Skip (no RICE)"
echo ""
read -p "  Choice [1]: " rice_choice
rice_choice="${rice_choice:-1}"

if [ "$rice_choice" -eq "$RICE_NUM" ] 2>/dev/null; then
    info "No RICE selected"
elif [ "$rice_choice" -ge 1 ] && [ "$rice_choice" -lt "$RICE_NUM" ] 2>/dev/null; then
    selected_rice="${RICE_OPTS[$((rice_choice-1))]}"
    python3 "$SHADOW_DATA/_lib/cli.py" rice set "$selected_rice"
else
    warn "Invalid choice, skipping..."
fi

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
