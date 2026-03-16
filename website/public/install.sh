#!/bin/sh
# mm CLI installer — https://minimax.villamarket.ai/install
# Usage: curl -fsSL minimax.villamarket.ai/install | sh
#
# Self-contained: only requires Python 3.10+. Creates its own venv.
set -e

PACKAGE="minimax-agent"
INSTALL_DIR="$HOME/.local/share/mm"
BIN_DIR="$HOME/.local/bin"

echo ""
echo "  mm — MiniMax-M2.5 AI terminal agent"
echo "  https://minimax.villamarket.ai"
echo ""

# ── Check Python ───────────────────────────────────────────────────────
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        # Check version >= 3.10
        ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
        major=$(echo "$ver" | cut -d. -f1)
        minor=$(echo "$ver" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Error: Python 3.10+ is required but not found."
    echo ""
    echo "Install Python first:"
    echo "  macOS:  brew install python@3.12"
    echo "  Ubuntu: sudo apt install python3"
    echo "  Other:  https://www.python.org/downloads/"
    exit 1
fi

echo "Using $PYTHON ($($PYTHON --version 2>&1))"

# ── Create venv and install ────────────────────────────────────────────
echo "Installing to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR" "$BIN_DIR"

# Create or update the venv
if [ ! -f "$INSTALL_DIR/bin/python" ]; then
    "$PYTHON" -m venv "$INSTALL_DIR"
fi

# Install/upgrade the package
"$INSTALL_DIR/bin/pip" install --quiet --upgrade "$PACKAGE"

# Symlink binaries
ln -sf "$INSTALL_DIR/bin/mm" "$BIN_DIR/mm" 2>/dev/null || true
ln -sf "$INSTALL_DIR/bin/minimax" "$BIN_DIR/minimax" 2>/dev/null || true

echo ""

# ── Verify ─────────────────────────────────────────────────────────────
if command -v mm >/dev/null 2>&1; then
    echo "Installed: $(mm --version)"
elif [ -x "$BIN_DIR/mm" ]; then
    echo "Installed: $("$BIN_DIR/mm" --version)"
    echo ""
    echo "Add this to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
else
    echo "Error: Installation failed."
    exit 1
fi

echo ""
echo "Get started:"
echo "  mm auth login     # Set your API key"
echo "  mm run            # Start chatting"
echo "  mm term           # Launch Toad TUI"
echo "  mm loop 'task'    # Ralph Loop (iterative dev)"
echo "  mm skills list    # List bundled skills"
echo ""
echo "Docs: https://minimax.villamarket.ai/docs"
