# Contributing to MiniMax CLI

## Quick Start

```bash
# Clone
git clone https://github.com/gastown-publish/minimax.git
cd minimax

# Install in dev mode
pip install -e ".[all]"

# Verify
mm --version
mm --help
```

---

## Getting a Test API Key

You need a valid API key to run tests. There are three ways to get one:

### Option A: Admin TUI (server operators only)

If you have access to the MiniMax server (LiteLLM running on port 4000):

```bash
# Set the LiteLLM master key
export LITELLM_MASTER_KEY="sk-your-master-key"

# Launch the admin TUI
mm tui

# Press 'g' to generate a new key
# The key will appear in the output area — copy it
# Optionally press 'e' to email it
```

The TUI creates keys via the LiteLLM `/key/generate` API:

```bash
# Or generate directly via curl:
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"models": ["minimax-m2.5"], "metadata": {"alias": "test-key"}}'
```

### Option B: Website dashboard

1. Go to [minimax.villamarket.ai/login](https://minimax.villamarket.ai/login)
2. Sign in with Google, Apple, or email/password
3. Navigate to Dashboard > API Keys
4. Click "Create Key"

### Option C: Ask a maintainer

Open an issue or DM a maintainer to request a test key.

### Store your key

```bash
mm auth login --key sk-your-test-key

# Verify it works
mm auth status
# Output: Key: sk-your-t...t-key
#         Status: valid
```

The key is stored at `~/.config/minimax/config.json` with `600` permissions.

For CI/testing, set the environment variable instead:

```bash
export MINIMAX_API_KEY=sk-your-test-key
```

---

## Testing

### Test Matrix

Every change MUST be tested in **both** environments:

| Environment | How to run | What it tests |
|-------------|-----------|---------------|
| **Docker** | `tests/e2e-client.sh` inside container | Fresh install, no local tools, public API only |
| **Local (non-Docker)** | `pip install -e .` then run tests | Dev install, local tools, may hit local server |

### Why both?

Docker tests catch:
- Leaked server paths (`/home/nic/...`)
- Leaked internal URLs (`localhost:4000`, Tailscale)
- Missing dependencies in Docker images
- Broken install scripts

Local tests catch:
- Import errors in editable installs
- Config file permission issues
- Tool binary resolution (`shutil.which`)
- Shell completion behavior

### Running Tests

#### 1. Docker E2E (required before every PR)

Tests all CLI commands from a fresh user perspective with zero local access:

```bash
# Build test image
docker build -t mm-test -f Dockerfile .

# Run full E2E suite
docker run --rm \
  -e API_KEY=sk-your-test-key \
  -v $(pwd)/tests:/tests:ro \
  python:3.12-slim \
  bash -c "pip install minimax-agent && bash /tests/e2e-client.sh"

# Or use the dev install:
docker run --rm \
  -e API_KEY=sk-your-test-key \
  -v $(pwd):/src:ro \
  python:3.12-slim \
  bash -c "pip install /src && bash /src/tests/e2e-client.sh"
```

This runs 16 test groups (~100 test cases):
- Installation and version
- Help text for all commands
- Auth flow (login/status/logout)
- API connectivity
- Live chat (real inference)
- Setup commands for all tools
- Launch commands (dry validation)
- Localhost reference detection (blocklist)
- Error messages and config integrity

#### 2. Docker Launch Tests (required for launch changes)

Tests all `mm launch` commands with Docker + tmux:

```bash
docker run --rm -it \
  -e TEST_API_KEY=sk-your-test-key \
  -v $(pwd):/src:ro \
  -v /var/run/docker.sock:/var/run/docker.sock \
  python:3.12-slim \
  bash -c "pip install /src && apt-get update && apt-get install -y tmux docker.io && bash /src/tests/docker-launch-test.sh"
```

Tests each tool (claude, aider, codex, opencode, openclaw, nori, toad, kimi):
- Docker image pulls successfully
- Config files are generated correctly
- API key is passed through
- Tool starts without crash

#### 3. Local Tests (required for every PR)

```bash
# Install in dev mode
pip install -e ".[all]"

# Verify CLI loads
mm --version
mm --help

# Verify auth works
export MINIMAX_API_KEY=sk-your-test-key
mm auth status

# Verify key connectivity
mm launch claude --no-docker --help  # Just check help loads
mm launch aider --no-docker --help
mm launch codex --no-docker --help

# Test shell completion
mm completion bash > /dev/null && echo "PASS: bash completion"
mm completion zsh > /dev/null && echo "PASS: zsh completion"

# Test upgrade check (doesn't actually upgrade)
mm upgrade  # Should show "Already up to date" or upgrade
```

#### 4. Infrastructure Tests (optional, for server ops)

```bash
# Test public endpoints
./scripts/test-tools.sh

# Test with authenticated calls
./scripts/test-tools.sh sk-your-test-key

# Test vLLM inference (requires local server)
./scripts/test.sh
```

---

## Docker Image Testing

When modifying any `docker/*.Dockerfile`:

### Build locally first

```bash
# Build the specific image
docker build -t mm-toad-test -f docker/toad.Dockerfile .

# Verify the full toolchain is present
docker run --rm mm-toad-test which claude     # Claude Code
docker run --rm mm-toad-test which nori       # Nori
docker run --rm mm-toad-test which mm         # mm CLI
docker run --rm mm-toad-test which toad       # Primary tool
docker run --rm mm-toad-test ls /root/.claude/skills/  # Skills
docker run --rm mm-toad-test cat /root/.mm-claude/CLAUDE.md  # System prompt

# Test interactively
docker run --rm -it -e MINIMAX_API_KEY=sk-test mm-toad-test --version
```

### Required checks for ALL Docker images

Every image MUST have (see [issue #4](https://github.com/gastown-publish/minimax/issues/4)):

- [ ] Primary tool binary works
- [ ] `claude` binary exists
- [ ] `nori` binary exists
- [ ] `mm` binary exists
- [ ] `/root/.claude/skills/` has skill files
- [ ] `/root/.mm-claude/CLAUDE.md` exists
- [ ] `nori-skillsets` installed with `senior-swe`
- [ ] Playwright MCP registered

---

## Version Management

**Single source of truth**: `pyproject.toml`

```bash
# Bump version (use the script!)
./scripts/bump-version.sh 0.2.11

# NEVER hardcode __version__ in Python files
# NEVER change version in __init__.py — it reads from metadata
```

CI checks (`ci.yml`) will fail if:
- `__init__.py` has a hardcoded version string
- Wheel version doesn't match `pyproject.toml`
- Installed version doesn't match `pyproject.toml`

---

## Release Checklist

1. Run Docker E2E tests: `tests/e2e-client.sh`
2. Run local tests: `mm --version && mm --help && mm auth status`
3. Bump version: `./scripts/bump-version.sh X.Y.Z`
4. Commit: `git add pyproject.toml && git commit -m "v0.2.X"`
5. Push: `git push origin main`
6. Create release: `gh release create vX.Y.Z --generate-notes`
7. Verify CI passes (build + pypi + deb + docker)
8. Verify Docker images rebuild: check `gh run list`

---

## Code Style

- Python 3.10+ (type hints, f-strings, `|` union syntax)
- Click for CLI commands
- Rich for terminal output
- No external linters enforced (yet) — just be consistent
- Keep launch.py functions focused: each tool gets one click command
- System prompts in `system_prompt.py` — never inline

---

## Project Rules

See [issue #6](https://github.com/gastown-publish/minimax/issues/6) for the full list. Key rules:

1. **Version**: `pyproject.toml` only. `importlib.metadata` at runtime.
2. **Docker images**: ALL must have full toolchain (Claude Code, Nori, Playwright MCP, skills, system prompt).
3. **Docker Hub**: `thanakijwanavit/mm-{tool}:latest` — public, no auth to pull.
4. **PyPI**: Package name is `minimax-agent`. Publishing may be broken — use GitHub Releases.
5. **API keys**: Bearer token, stored at `~/.config/minimax/config.json` with `600` perms.
6. **System prompts**: `SYSTEM_PROMPT` (generic) + `CLAUDE_SYSTEM_PROMPT` (Claude-specific) in `system_prompt.py`.
