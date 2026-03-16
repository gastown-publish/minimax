# Homebrew Tap for mm

## Setup

1. Create the tap repo: `gh repo create gastown-publish/homebrew-mm --public`
2. Copy `mm.rb` into the tap repo root
3. Fill in SHA256 hashes from the release tarball and PyPI packages
4. Users install with:

```bash
brew tap gastown-publish/mm
brew install mm
```

## Updating

After each release:
1. Update `url` and `sha256` in mm.rb
2. Update resource versions/hashes as needed
3. Push to the tap repo
