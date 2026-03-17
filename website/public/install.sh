#!/bin/sh
# mm CLI installer — https://minimax.villamarket.ai/install
# Usage: curl -fsSL minimax.villamarket.ai/install | sh
#
# Self-contained: only requires Python 3.10+ and curl.
# Downloads wheel from GitHub Releases, installs in its own venv.
# Safe to re-run — removes old version before installing new one.
set -e

REPO="gastown-publish/minimax"
INSTALL_DIR="$HOME/.local/share/mm"
BIN_DIR="$HOME/.local/bin"

echo ""
echo "  mm — MiniMax-M2.5 AI terminal agent"
echo "  https://minimax.villamarket.ai"
echo ""

# ── Check curl ────────────────────────────────────────────────────────
if ! command -v curl >/dev/null 2>&1; then
    echo "Error: curl is required but not found."
    exit 1
fi

# ── Check Python ───────────────────────────────────────────────────────
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
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

# ── Remove old installations ─────────────────────────────────────────
# Remove old user-level pip install (if any)
for pip_cmd in pip3 pip; do
    if command -v "$pip_cmd" >/dev/null 2>&1; then
        if "$pip_cmd" show minimax-agent >/dev/null 2>&1; then
            echo "Removing old pip install of minimax-agent..."
            "$pip_cmd" uninstall -y minimax-agent 2>/dev/null || true
        fi
    fi
done

# Remove stale symlinks
for bin_name in mm minimax; do
    target="$BIN_DIR/$bin_name"
    if [ -L "$target" ]; then
        # Check if symlink points to a dead target
        if [ ! -e "$target" ]; then
            echo "Removing stale symlink: $target"
            rm -f "$target"
        fi
    fi
done

# Remove old venv to ensure clean install
if [ -d "$INSTALL_DIR" ]; then
    OLD_VER=""
    if [ -x "$INSTALL_DIR/bin/mm" ]; then
        OLD_VER=$("$INSTALL_DIR/bin/mm" --version 2>/dev/null || echo "unknown")
    fi
    echo "Removing old installation${OLD_VER:+ ($OLD_VER)}..."
    rm -rf "$INSTALL_DIR"
fi

# ── Find latest wheel from GitHub Releases ────────────────────────────
echo "Fetching latest release from GitHub..."
WHEEL_URL=$("$PYTHON" -c "
import json, sys, urllib.request
url = 'https://api.github.com/repos/$REPO/releases/latest'
req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json'})
data = json.loads(urllib.request.urlopen(req).read())
for asset in data.get('assets', []):
    if asset['name'].endswith('.whl'):
        print(asset['browser_download_url'])
        sys.exit(0)
print('', end='')
sys.exit(1)
" 2>/dev/null) || true

if [ -z "$WHEEL_URL" ]; then
    echo "Error: Could not find wheel in latest GitHub release."
    echo "Check: https://github.com/$REPO/releases"
    exit 1
fi

echo "Found: $(basename "$WHEEL_URL")"

# ── Download wheel ────────────────────────────────────────────────────
TMPDIR=$(mktemp -d)
WHEEL_FILE="$TMPDIR/$(basename "$WHEEL_URL")"
echo "Downloading..."
curl -fsSL -o "$WHEEL_FILE" "$WHEEL_URL"

# ── Create venv and install ───────────────────────────────────────────
echo "Installing to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR" "$BIN_DIR"

# Create fresh venv
"$PYTHON" -m venv "$INSTALL_DIR"

# Install the wheel directly (no PyPI needed)
"$INSTALL_DIR/bin/pip" install --quiet "$WHEEL_FILE"

# Cleanup
rm -rf "$TMPDIR"

# Symlink binaries
ln -sf "$INSTALL_DIR/bin/mm" "$BIN_DIR/mm" 2>/dev/null || true
ln -sf "$INSTALL_DIR/bin/minimax" "$BIN_DIR/minimax" 2>/dev/null || true

echo ""

# ── Verify ────────────────────────────────────────────────────────────
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
echo "  mm term           # Launch Nori TUI"
echo "  mm launch claude  # Use with Claude Code"
echo "  mm skills list    # List bundled skills"
echo ""
echo "Docs: https://minimax.villamarket.ai/docs"
