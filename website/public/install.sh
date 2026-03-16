#!/bin/sh
# mm CLI installer — https://minimax.villamarket.ai/install
# Usage: curl -fsSL minimax.villamarket.ai/install | sh
set -e

echo "Installing mm (MiniMax CLI)..."
echo ""

# Detect package manager and install
if command -v uv >/dev/null 2>&1; then
    echo "Using uv..."
    uv tool install -U mm-cli
elif command -v pipx >/dev/null 2>&1; then
    echo "Using pipx..."
    pipx install mm-cli
elif command -v pip >/dev/null 2>&1; then
    echo "Using pip..."
    pip install --user mm-cli
elif command -v pip3 >/dev/null 2>&1; then
    echo "Using pip3..."
    pip3 install --user mm-cli
else
    echo "Error: No Python package manager found."
    echo "Install one of: uv, pipx, pip (Python 3.10+)"
    exit 1
fi

echo ""

# Verify installation
if command -v mm >/dev/null 2>&1; then
    echo "Installed: $(mm --version)"
    echo ""
    echo "Get started:"
    echo "  mm auth login     # Set your API key"
    echo "  mm run            # Start chatting"
    echo "  mm term           # Launch Toad TUI"
    echo "  mm loop 'task'    # Ralph Loop (iterative dev)"
    echo "  mm skills list    # List bundled skills"
else
    echo "Warning: mm not found in PATH."
    echo "Add ~/.local/bin to your PATH:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
fi
