#!/bin/bash
# Build a .deb package for minimax-agent
set -euo pipefail

# Version from env var (CI sets this from release tag) or pyproject.toml
if [ -z "${VERSION:-}" ]; then
    VERSION=$(grep '^version' pyproject.toml 2>/dev/null | head -1 | sed 's/.*"\(.*\)".*/\1/' || echo "0.0.0")
fi
PKG="minimax-agent"
ARCH="all"  # Pure Python, architecture-independent
WORKDIR=$(mktemp -d)
DEB_ROOT="${WORKDIR}/${PKG}_${VERSION}_${ARCH}"

echo "Building ${PKG}_${VERSION}_${ARCH}.deb ..."

# Create directory structure
mkdir -p "${DEB_ROOT}/DEBIAN"
mkdir -p "${DEB_ROOT}/usr/lib/minimax-agent"
mkdir -p "${DEB_ROOT}/usr/bin"

# Control file
cat > "${DEB_ROOT}/DEBIAN/control" <<EOF
Package: ${PKG}
Version: ${VERSION}
Section: devel
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.10), python3-pip, python3-venv
Maintainer: villamarket.ai <noreply@villamarket.ai>
Description: MiniMax-M2.5 AI terminal agent
 Chat, code, run skills, and use the Ralph Loop — all from your terminal.
 Connects to the MiniMax-M2.5 API at api.minimax.villamarket.ai.
Homepage: https://minimax.villamarket.ai
EOF

# Post-install: create venv and install from PyPI
cat > "${DEB_ROOT}/DEBIAN/postinst" <<'EOF'
#!/bin/bash
set -e
VENV=/usr/lib/minimax-agent/venv
python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet minimax-agent
# Symlink binaries
ln -sf "$VENV/bin/mm" /usr/bin/mm
ln -sf "$VENV/bin/minimax" /usr/bin/minimax
echo "mm installed: $(mm --version)"
EOF
chmod 755 "${DEB_ROOT}/DEBIAN/postinst"

# Pre-remove: cleanup
cat > "${DEB_ROOT}/DEBIAN/prerm" <<'EOF'
#!/bin/bash
set -e
rm -f /usr/bin/mm /usr/bin/minimax
rm -rf /usr/lib/minimax-agent/venv
EOF
chmod 755 "${DEB_ROOT}/DEBIAN/prerm"

# Build .deb
dpkg-deb --build "${DEB_ROOT}"
mv "${DEB_ROOT}.deb" "./${PKG}_${VERSION}_${ARCH}.deb"
rm -rf "${WORKDIR}"

echo "Built: ${PKG}_${VERSION}_${ARCH}.deb"
echo ""
echo "Install with: sudo dpkg -i ${PKG}_${VERSION}_${ARCH}.deb"
echo "Or host on GitHub Releases and add an apt repo."
