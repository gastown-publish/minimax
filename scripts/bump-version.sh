#!/bin/bash
# Bump version in pyproject.toml (single source of truth)
# Usage: ./scripts/bump-version.sh 0.3.0
#
# The version is ONLY in pyproject.toml. At runtime, __init__.py
# reads it via importlib.metadata. No other files to update.

set -e

if [ -z "$1" ]; then
    CURRENT=$(python3 -c "import re; print(re.search(r'version = \"(.+?)\"', open('pyproject.toml').read()).group(1))")
    echo "Current version: $CURRENT"
    echo "Usage: $0 <new-version>"
    echo "Example: $0 0.3.0"
    exit 1
fi

NEW_VERSION="$1"
TOML="pyproject.toml"

# Update pyproject.toml
sed -i "s/^version = \".*\"/version = \"${NEW_VERSION}\"/" "$TOML"

echo "Version bumped to $NEW_VERSION"
echo ""
echo "Next steps:"
echo "  git add pyproject.toml"
echo "  git commit -m 'v${NEW_VERSION}'"
echo "  git push"
echo "  gh release create v${NEW_VERSION} --title 'v${NEW_VERSION}' --generate-notes"
