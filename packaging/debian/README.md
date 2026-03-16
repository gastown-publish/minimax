# Debian/Ubuntu Package for mm

## Building

```bash
chmod +x build-deb.sh
./build-deb.sh
# Produces: mm-cli_0.2.0_all.deb
```

## Installing

```bash
sudo dpkg -i mm-cli_0.2.0_all.deb
```

## Hosting an apt repo

Option A: **GitHub Releases** — upload .deb to each release, users download directly.

Option B: **S3 apt repo** — for `sudo apt install mm-cli`:

1. Install `reprepro`
2. Create S3-backed apt repo at `apt.minimax.villamarket.ai`
3. Add CloudFront + Route53 for the subdomain
4. Users add:
   ```bash
   echo "deb https://apt.minimax.villamarket.ai stable main" | sudo tee /etc/apt/sources.list.d/mm.list
   curl -fsSL https://apt.minimax.villamarket.ai/key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/mm.gpg
   sudo apt update && sudo apt install mm-cli
   ```

## How it works

The .deb postinst script creates a Python venv at `/usr/lib/mm-cli/venv`
and `pip install mm-cli` inside it. This avoids conflicts with system Python
packages while providing a clean `mm` binary at `/usr/bin/mm`.
