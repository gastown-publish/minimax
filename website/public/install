#!/bin/sh
# mm CLI installer — https://minimax.villamarket.ai/install
# Usage: curl -fsSL minimax.villamarket.ai/install | sh
set -e

VERSION="0.2.0"

echo ""
echo "  mm — MiniMax-M2.5 AI terminal agent"
echo "  https://minimax.villamarket.ai"
echo ""

# ── Install via best available Python tool ─────────────────────────────

installed=0

# 1. uv (fastest, isolated)
if [ "$installed" = 0 ] && command -v uv >/dev/null 2>&1; then
    echo "Installing with uv..."
    uv tool install -U mm-cli
    installed=1
fi

# 2. pipx (isolated)
if [ "$installed" = 0 ] && command -v pipx >/dev/null 2>&1; then
    echo "Installing with pipx..."
    pipx install mm-cli
    installed=1
fi

# 3. pip3 / pip
if [ "$installed" = 0 ]; then
    PIP=""
    if command -v pip3 >/dev/null 2>&1; then
        PIP="pip3"
    elif command -v pip >/dev/null 2>&1; then
        PIP="pip"
    fi

    if [ -n "$PIP" ]; then
        echo "Installing with ${PIP}..."
        $PIP install --user mm-cli
        installed=1
    fi
fi

# 4. Nothing worked — suggest installing uv
if [ "$installed" = 0 ]; then
    echo "No Python package manager found (uv, pipx, or pip)."
    echo ""
    echo "Install uv first (recommended):"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "Then re-run this installer, or just:"
    echo "  uv tool install mm-cli"
    exit 1
fi

echo ""

# ── Verify ─────────────────────────────────────────────────────────────
if command -v mm >/dev/null 2>&1; then
    echo "Installed: $(mm --version)"
    echo ""
    echo "Get started:"
    echo "  mm auth login     # Set your API key"
    echo "  mm run            # Start chatting"
    echo "  mm term           # Launch Toad TUI"
    echo "  mm loop 'task'    # Ralph Loop (iterative dev)"
    echo "  mm skills list    # List bundled skills"
    echo ""
    echo "Docs: https://minimax.villamarket.ai/docs"
else
    echo "Warning: mm not found in PATH."
    echo ""
    echo "Try adding this to your shell profile:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
    echo ""
    echo "Then run: mm --version"
fi
