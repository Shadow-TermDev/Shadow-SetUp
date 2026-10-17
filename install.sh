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

trap 'echo -e "\n${YELLOW}[!!]${NC} Cancelled — install left partial. Re-run install.sh to repair."; exit 1' INT

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
# Helpers — bin dir + PATH idempotency
# -----------------------------------------------
# Always (re)create ~/.local/bin so wrappers never land on a missing dir.
ensure_bin_dir() {
    mkdir -p "$SHADOW_BIN" 2>/dev/null
    [ -d "$SHADOW_BIN" ] || fail "Cannot create $SHADOW_BIN"
}

# Add ~/.local/bin to one rc file if it is not exported there yet.
# Idempotent, so reinstalling never duplicates the line.
ensure_path_in_rc() {
    local rc="$1"
    [ -n "$rc" ] || return 0
    [ -f "$rc" ] || touch "$rc" 2>/dev/null || return 0
    grep -q '\.local/bin' "$rc" 2>/dev/null && return 0
    printf '\n%s\n%s\n' '# Shadow-SetUp PATH' 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc"
    PATH_CHANGED=1
}

# Verify PATH landed in the rc files the user can actually boot with (zsh + bash).
# Called more than once: Oh My Zsh may rewrite ~/.zshrc after this runs.
ensure_shell_path() {
    PATH_CHANGED=0
    ensure_path_in_rc "$HOME/.zshrc"
    ensure_path_in_rc "$HOME/.bashrc"
    if [ "$PATH_CHANGED" -eq 1 ]; then
        ok "PATH added to shell rc"
    fi
}

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
mkdir -p "$SHADOW_DATA" "$SHADOW_DATA/cache" "$SHADOW_DATA/backups"
ensure_bin_dir
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

# Bundled RICEs live in the cloned repo (used by the offline copy + selection steps)
REPO_RICES="$TEMP_DIR/dotfiles/rices"

# -----------------------------------------------
# Install files (EXCEPT rices — handled later)
# -----------------------------------------------
info "Installing files..."

[ -d "$TEMP_DIR/_lib" ] || fail "Repository is missing _lib/ — cannot install CLI"
rm -rf "$SHADOW_DATA/_lib"
cp -r "$TEMP_DIR/_lib" "$SHADOW_DATA/_lib"
[ -f "$SHADOW_DATA/_lib/cli.py" ] || fail "CLI install failed (_lib/cli.py missing)"
ok "_lib installed"

if [ -d "$TEMP_DIR/dotfiles" ]; then
    # Preserve existing rices before overwriting
    EXISTING_RICES=""
    RICES_SAFE=false
    if [ -d "$SHADOW_DATA/dotfiles/rices" ]; then
        # cache/ may be missing on a partial install — never lose local RICEs
        mkdir -p "$SHADOW_DATA/cache"
        EXISTING_RICES="$SHADOW_DATA/cache/existing_rices_backup"
        rm -rf "$EXISTING_RICES"
        if cp -r "$SHADOW_DATA/dotfiles/rices" "$EXISTING_RICES"; then
            RICES_SAFE=true
        else
            warn "Could not back up existing RICEs — keeping them in place"
        fi
    fi

    # Wipe only when the local RICEs are safely backed up
    if [ "$RICES_SAFE" = true ] || [ ! -d "$SHADOW_DATA/dotfiles/rices" ]; then
        rm -rf "$SHADOW_DATA/dotfiles"
    else
        warn "Keeping existing dotfiles (RICE backup failed)"
    fi
    mkdir -p "$SHADOW_DATA/dotfiles"
    # Copy everything EXCEPT rices directory.
    # dotglob is required: without it hidden dotfiles (.zshrc, .nanorc,
    # .p10k.zsh, .termux/) are skipped by the glob and the RICE never gets sourced.
    shopt -s dotglob nullglob
    for item in "$TEMP_DIR/dotfiles"/*; do
        item_name=$(basename "$item")
        [ "$item_name" = "rices" ] && continue
        cp -r "$item" "$SHADOW_DATA/dotfiles/"
    done
    shopt -u dotglob nullglob
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
    # Belt and braces: guarantee the framework dotfiles are present,
    # no matter what the glob above did.
    for required in .zshrc .nanorc; do
        if [ -f "$TEMP_DIR/dotfiles/$required" ]; then
            cp -f "$TEMP_DIR/dotfiles/$required" "$SHADOW_DATA/dotfiles/$required" \
                || fail "Failed to install dotfiles/$required"
        fi
    done
    [ -f "$SHADOW_DATA/dotfiles/.zshrc" ] || warn ".zshrc not installed — shell module will not load RICEs"
    ok "dotfiles installed"
fi

# Ship every bundled RICE so `sw rice set <name>` works offline.
# Existing local RICEs (possibly customized) are never overwritten.
if [ -d "$REPO_RICES" ]; then
    for d in "$REPO_RICES"/*; do
        [ -d "$d" ] || continue
        rname=$(basename "$d")
        [ -f "$d/rice.sh" ] || [ -f "$d/manifest.json" ] || continue
        if [ ! -d "$SHADOW_DATA/dotfiles/rices/$rname" ]; then
            mkdir -p "$SHADOW_DATA/dotfiles/rices"
            cp -r "$d" "$SHADOW_DATA/dotfiles/rices/" && ok "RICE '$rname' bundled"
        fi
    done
fi

[ -f "$TEMP_DIR/.version" ] && { cp "$TEMP_DIR/.version" "$SHADOW_DATA/.version"; ok ".version installed"; }

# -----------------------------------------------
# CLI wrappers
# -----------------------------------------------
info "Creating CLI commands..."
# Re-create the bin dir: this step must survive partial/interrupted installs
ensure_bin_dir
[ -f "$SHADOW_DATA/_lib/cli.py" ] || fail "CLI missing at $SHADOW_DATA/_lib/cli.py"
for cmd in sw shadow; do
    cat > "$SHADOW_BIN/$cmd" << EOF || fail "Cannot write wrapper '$cmd' in $SHADOW_BIN"
#!/data/data/com.termux/files/usr/bin/bash
exec python3 "$SHADOW_DATA/_lib/cli.py" "\$@"
EOF
    chmod +x "$SHADOW_BIN/$cmd" || fail "Cannot make '$cmd' executable"
    [ -x "$SHADOW_BIN/$cmd" ] || fail "Wrapper '$cmd' is not executable"
    ok "Command '$cmd' created"
done
# Make the new commands usable in this very session
export PATH="$SHADOW_BIN:$PATH"

# -----------------------------------------------
# PATH
# -----------------------------------------------
info "Setting up PATH..."
ensure_shell_path

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

# Install each module in its own process: a crash in one of them (e.g. a
# network timeout in shell) must never skip the remaining modules.
install_modules() {
    for module in "$@"; do
        info "Installing module: $module"
        python3 "$SHADOW_DATA/_lib/cli.py" install "$module" < /dev/tty \
            || warn "Module '$module' reported problems — continuing with the rest"
    done
}

case "$choice" in
    1) install_modules shell tools dotfiles aliases ;;
    2) install_modules shell tools ;;
    3) info "Skipping module install" ;;
    *) install_modules shell tools dotfiles aliases ;;
esac

# Oh My Zsh may have rewritten ~/.zshrc above — make sure PATH survived
ensure_shell_path

# -----------------------------------------------
# Shell verification — zsh + Oh My Zsh + login shell
# -----------------------------------------------
# A slow network can fail part of the shell module; that must not leave the
# user stuck on bash. Advisory only: never abort the installer here.
verify_shell() {
    if ! command -v zsh &>/dev/null; then
        warn "zsh is not installed — retry with: sw install shell"
        return 1
    fi
    [ -d "$HOME/.oh-my-zsh" ] \
        || warn "Oh My Zsh missing (slow network?) — retry with: sw install shell"
    [ -d "$HOME/.oh-my-zsh/custom/themes/powerlevel10k" ] \
        || warn "Powerlevel10k missing — theme falls back to robbyrussell. Retry: sw install shell"
    # The framework .zshrc must be in place (or at least source the RICE)
    if [ -f "$SHADOW_DATA/dotfiles/.zshrc" ] && ! grep -q 'active_rice.sh' "$HOME/.zshrc" 2>/dev/null; then
        warn "~/.zshrc does not source the RICE — run: sw install dotfiles"
    fi
    return 0
}

# Land in zsh on the next session even when p10k/plugins failed
ensure_login_shell() {
    command -v zsh &>/dev/null || return 0
    case "${SHELL:-}" in
        */zsh) return 0 ;;
    esac
    info "Setting zsh as default shell..."
    if command -v chsh &>/dev/null && chsh -s zsh 2>/dev/null; then
        ok "Default shell is now zsh — open a new session (or run: exec zsh)"
    else
        warn "Could not change the default shell — run: chsh -s zsh"
    fi
}

# Offer an immediate retry when Oh My Zsh is missing: on a slow link this is
# the difference between a themed prompt and a bare zsh "%".
retry_shell_if_broken() {
    command -v zsh &>/dev/null || return 0
    [ -d "$HOME/.oh-my-zsh" ] && return 0
    echo ""
    warn "Oh My Zsh did not install — the prompt will fall back to plain zsh."
    read -p "  Retry now? [Y/n]: " retry_input < /dev/tty || return 0
    case "${retry_input:-Y}" in
        [nN]*) info "Skipping retry — run later: sw install shell" ;;
        *)
            info "Retrying shell install..."
            python3 "$SHADOW_DATA/_lib/cli.py" install shell < /dev/tty \
                || warn "Retry failed — run later: sw install shell"
            ;;
    esac
    [ -d "$HOME/.oh-my-zsh" ] \
        || warn "Oh My Zsh still missing — the shell works but the prompt stays plain zsh. Fix with: sw install shell"
}

if [ "$choice" != "3" ]; then
    verify_shell
    ensure_login_shell
    retry_shell_if_broken
fi

# -----------------------------------------------
# RICE selection — SELECT WHICH ONE TO ACTIVATE
# -----------------------------------------------
echo ""
echo -e "${BOLD}--- RICE Selection ---${NC}"
echo ""

# Helper: guarantee a usable RICE — activate the default one when none is active
install_default_if_needed() {
    LOCAL_RICES="$SHADOW_DATA/dotfiles/rices"
    ACTIVE_NAME_FILE="$SHADOW_DATA/active_rice_name"
    ACTIVE_LINK="$SHADOW_DATA/active_rice.sh"

    # Something is already active and wired up — leave it alone
    if [ -s "$ACTIVE_NAME_FILE" ] && [ -f "$ACTIVE_LINK" ]; then
        info "RICEs exist — keeping current setup"
        return
    fi

    TARGET="default"
    if [ ! -d "$LOCAL_RICES/$TARGET" ] && [ -d "$REPO_RICES/$TARGET" ]; then
        mkdir -p "$LOCAL_RICES"
        cp -r "$REPO_RICES/$TARGET" "$LOCAL_RICES/"
    fi

    if [ -d "$LOCAL_RICES/$TARGET" ]; then
        info "No active RICE — installing default..."
        python3 "$SHADOW_DATA/_lib/cli.py" rice set "$TARGET" < /dev/tty
    else
        warn "No RICE available — skipping"
    fi
}

RICE_LIST=()

if [ -d "$REPO_RICES" ]; then
    # Use find instead of glob for reliability — check for rice.sh OR manifest.json
    while IFS= read -r d; do
        if [ -f "$d/rice.sh" ] || [ -f "$d/manifest.json" ]; then
            RICE_LIST+=("$(basename "$d")")
        fi
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
        # Copy ONLY if missing — `cp -r src dst/` into an existing dir would nest it
        if [ ! -d "$SHADOW_DATA/dotfiles/rices/$PICKED" ]; then
            mkdir -p "$SHADOW_DATA/dotfiles/rices"
            cp -r "$REPO_RICES/$PICKED" "$SHADOW_DATA/dotfiles/rices/" \
                || warn "Could not copy RICE '$PICKED' from repo"
        fi
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
# Final verification — wrappers + PATH must survive the whole run
# -----------------------------------------------
ensure_bin_dir
for cmd in sw shadow; do
    [ -x "$SHADOW_BIN/$cmd" ] || fail "Wrapper '$cmd' missing or broken — re-run install.sh"
done
ensure_shell_path
export PATH="$SHADOW_BIN:$PATH"
command -v sw &>/dev/null || warn "'sw' not in PATH for new sessions yet — open a new terminal"

# -----------------------------------------------
# Final
# -----------------------------------------------
# One-line shell status so a partial install is never a surprise
if command -v zsh &>/dev/null && [ -d "$HOME/.oh-my-zsh" ]; then
    ok "Shell ready (zsh + Oh My Zsh)"
elif command -v zsh &>/dev/null; then
    warn "Shell partial — Oh My Zsh missing. Fix with: sw install shell"
else
    warn "zsh not installed — the session stays on bash. Fix with: sw install shell"
fi

echo ""
echo -e "${GREEN}${BOLD}Installation complete!${NC}"
echo ""
echo -e "  Run: ${BOLD}sw${NC}           # Interactive menu"
echo -e "  Or: ${BOLD}sw help${NC}       # Show commands"
echo ""
echo -e "  ${DIM}Shadow-TermDev · https://Shadow-TermDev.github.io${NC}"
echo ""
