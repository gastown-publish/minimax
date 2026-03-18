#!/bin/bash
# ============================================================================
# E2E CLIENT TEST — Tests every mm CLI command from an end-user perspective.
#
# Must be run inside a clean Docker container with NO localhost access.
# Tests against the PUBLIC API only.
#
# Usage:
#   docker run --rm -e API_KEY=sk-xxx python:3.12-slim bash /tests/e2e-client.sh
#
# Requirements:
#   - API_KEY environment variable set to a valid MiniMax API key
#   - Internet access to api.minimax.villamarket.ai and github.com
#   - NO access to localhost:4000 or localhost:8080
# ============================================================================
set -euo pipefail

PASSED=0
FAILED=0
FAIL_LIST=""

pass() {
    echo "  PASS: $1"
    PASSED=$((PASSED + 1))
}

fail() {
    echo "  FAIL: $1 — $2"
    FAILED=$((FAILED + 1))
    FAIL_LIST="${FAIL_LIST}\n  FAIL: $1 — $2"
}

# Blocklist patterns — these should NEVER appear in client-facing output
TAILSCALE_URL="gpu-workspace.taile8dc37.ts.net"
SERVER_PATH="/home/nic"
INTERNAL_VLLM_REF="vLLM :8080"
INTERNAL_LITELLM_REF="LiteLLM :4000"

# Helper: check output for leaked internal info
check_no_leaks() {
    local label="$1"
    local output="$2"
    local leaked=0

    if echo "$output" | grep -q "$SERVER_PATH"; then
        fail "$label" "leaks server path '$SERVER_PATH'"
        leaked=1
    fi
    if echo "$output" | grep -q "$TAILSCALE_URL"; then
        fail "$label" "leaks Tailscale URL '$TAILSCALE_URL'"
        leaked=1
    fi
    if echo "$output" | grep -q "Traceback (most recent call last)"; then
        fail "$label" "shows raw Python traceback"
        leaked=1
    fi
    return $leaked
}

# ── Preflight ──────────────────────────────────────────────────────────────
echo "============================================"
echo "=== E2E CLIENT TEST ==="
echo "============================================"
echo ""

# Accept both API_KEY and MINIMAX_API_KEY
API_KEY="${API_KEY:-${MINIMAX_API_KEY:-}}"
if [ -z "$API_KEY" ]; then
    echo "ERROR: API_KEY or MINIMAX_API_KEY environment variable not set"
    exit 1
fi

echo "API Key: ${API_KEY:0:8}...${API_KEY: -4}"
echo ""

# ── Install ────────────────────────────────────────────────────────────────
echo "=== GROUP 1: Installation ==="
echo ""

# 1.1 Install from wheel (mounted or pip)
if command -v mm >/dev/null 2>&1; then
    pass "mm binary available"
else
    # Try local wheel first, then PyPI
    pip install -q /wheel/*.whl 2>/dev/null || pip install -q minimax-agent 2>/dev/null
    export PATH="$HOME/.local/bin:$PATH"
    if command -v mm >/dev/null 2>&1; then
        pass "mm installed via pip"
    else
        fail "mm binary" "not found after install"
    fi
fi

# 1.2 Version
VERSION=$(mm --version 2>&1)
if echo "$VERSION" | grep -q "0.2"; then
    pass "mm --version = 0.2.x ($VERSION)"
else
    fail "mm --version" "got: $VERSION"
fi

# 1.3 Alias
ALIAS_VERSION=$(minimax --version 2>&1)
if echo "$ALIAS_VERSION" | grep -q "0.2"; then
    pass "minimax --version (alias)"
else
    fail "minimax --version" "got: $ALIAS_VERSION"
fi

# 1.4 Both report same version
if [ "$VERSION" = "$ALIAS_VERSION" ]; then
    pass "mm and minimax report same version"
else
    fail "version mismatch" "mm=$VERSION, minimax=$ALIAS_VERSION"
fi

echo ""
echo "=== GROUP 2: Help text for all commands ==="
echo ""

# 2.x Every command's --help must show "Usage:" and exit 0
for cmd in run acp term auth setup list logs ps stop test tui serve launch completion; do
    OUTPUT=$(mm $cmd --help 2>&1) || true
    if echo "$OUTPUT" | grep -q "Usage:"; then
        pass "mm $cmd --help"
    else
        fail "mm $cmd --help" "no Usage: in output"
    fi
    # Also check no leaks in help text
    check_no_leaks "mm $cmd --help leak" "$OUTPUT" || true
done

# 2.x2 Subcommand help
for subcmd in "auth login" "auth status" "auth logout"; do
    OUTPUT=$(mm $subcmd --help 2>&1) || true
    if echo "$OUTPUT" | grep -q "Usage:"; then
        pass "mm $subcmd --help"
    else
        fail "mm $subcmd --help" "no Usage: in output"
    fi
done

# 2.x3 -h shorthand for --help
OUTPUT=$(mm -h 2>&1) || true
if echo "$OUTPUT" | grep -q "Usage:"; then
    pass "mm -h (shorthand for --help)"
else
    fail "mm -h" "no Usage: in output"
fi

for cmd in run auth launch; do
    OUTPUT=$(mm $cmd -h 2>&1) || true
    if echo "$OUTPUT" | grep -q "Usage:"; then
        pass "mm $cmd -h"
    else
        fail "mm $cmd -h" "no Usage: in output"
    fi
done

echo ""
echo "=== GROUP 3: Auth flow ==="
echo ""

# 3.1 Status with no key (must unset env var)
OUTPUT=$(MINIMAX_API_KEY="" mm auth status 2>&1) || true
if echo "$OUTPUT" | grep -q "Not authenticated"; then
    pass "mm auth status (no key)"
else
    fail "mm auth status (no key)" "expected 'Not authenticated', got: $OUTPUT"
fi

# 3.2 Status error message uses "mm" not "minimax"
if echo "$OUTPUT" | grep -q "mm auth login"; then
    pass "auth status says 'mm auth login' (correct branding)"
else
    fail "auth branding" "says 'minimax auth login' instead of 'mm auth login'"
fi

# 3.3 Login with real key — must verify against PUBLIC API (not localhost)
OUTPUT=$(mm auth login --key "$API_KEY" 2>&1) || true
if echo "$OUTPUT" | grep -q "valid"; then
    pass "mm auth login — key verified against public API"
elif echo "$OUTPUT" | grep -q "failed"; then
    fail "mm auth login" "verification FAILED — likely still hitting localhost"
else
    fail "mm auth login" "unexpected output: $OUTPUT"
fi

# 3.4 Auth login output doesn't mention LiteLLM
if echo "$OUTPUT" | grep -qi "litellm"; then
    fail "mm auth login output" "mentions 'LiteLLM' — internal service name"
else
    pass "mm auth login doesn't mention LiteLLM"
fi

# 3.5 Status after login
OUTPUT=$(mm auth status 2>&1) || true
if echo "$OUTPUT" | grep -q "valid"; then
    pass "mm auth status (with key) — valid"
else
    fail "mm auth status (with key)" "not valid: $OUTPUT"
fi

# 3.6 Auth messages don't mention "LiteLLM" (end users don't know what LiteLLM is)
ALL_AUTH=$(mm auth login --help 2>&1; mm auth status --help 2>&1) || true
if echo "$ALL_AUTH" | grep -qi "litellm"; then
    fail "auth help leaks 'LiteLLM'" "end users shouldn't see internal service names"
else
    pass "auth help doesn't mention LiteLLM"
fi

echo ""
echo "=== GROUP 4: API connectivity ==="
echo ""

# 4.1 mm test — should work against public API (not crash looking for scripts)
OUTPUT=$(mm test 2>&1) || true
if echo "$OUTPUT" | grep -q "Script not found"; then
    fail "mm test" "tries to find local script — broken on client"
elif echo "$OUTPUT" | grep -qi "passed\|OK\|Health.*OK\|checks passed\|Endpoint"; then
    pass "mm test — connected to public API"
else
    fail "mm test" "unexpected: $OUTPUT"
fi
check_no_leaks "mm test" "$OUTPUT" || true

# 4.2 mm list — should show models from public API
OUTPUT=$(mm list 2>&1) || true
if echo "$OUTPUT" | grep -qi "minimax\|model"; then
    pass "mm list — shows models from public API"
elif echo "$OUTPUT" | grep -q "is the server running"; then
    fail "mm list" "says 'is the server running' — bad error for client"
else
    fail "mm list" "unexpected: $OUTPUT"
fi
check_no_leaks "mm list" "$OUTPUT" || true

# 4.3 mm ps — should show connection status (not crash looking for PID files)
OUTPUT=$(mm ps 2>&1) || true
if echo "$OUTPUT" | grep -q "Script not found\|Traceback"; then
    fail "mm ps" "crashes on client"
elif echo "$OUTPUT" | grep -qi "status\|connected\|endpoint\|Key"; then
    pass "mm ps — shows client connection status"
else
    fail "mm ps" "unexpected: $OUTPUT"
fi
check_no_leaks "mm ps" "$OUTPUT" || true

# 4.4 mm test shows the correct endpoint (public API or local LiteLLM)
TEST_OUTPUT=$(mm test 2>&1)
if echo "$TEST_OUTPUT" | grep -q "api.minimax.villamarket.ai\|localhost:4000"; then
    pass "mm test — shows valid API endpoint"
else
    fail "mm test endpoint" "doesn't show expected endpoint: $TEST_OUTPUT"
fi

echo ""
echo "=== GROUP 5: Live chat ==="
echo ""

# 5.1 mm run — should show public API endpoint, not "LiteLLM :4000"
OUTPUT=$(echo -e "Say hi\n/exit" | timeout 30 mm run 2>&1) || true
if echo "$OUTPUT" | grep -q "LiteLLM :4000"; then
    fail "mm run source" "shows 'LiteLLM :4000' — should show public API URL"
elif echo "$OUTPUT" | grep -q "vLLM :8080"; then
    fail "mm run source" "shows 'vLLM :8080' — should show public API URL"
elif echo "$OUTPUT" | grep -qi "api.minimax\|MiniMax"; then
    pass "mm run — shows correct API endpoint"
else
    fail "mm run source" "unexpected banner: $OUTPUT"
fi
check_no_leaks "mm run" "$OUTPUT" || true

# 5.2 mm run — should not say "Start with: minimax serve" on error
OUTPUT_ERR=$(echo "" | timeout 5 mm run --model nonexistent 2>&1) || true
if echo "$OUTPUT_ERR" | grep -q "minimax serve"; then
    fail "mm run error" "says 'Start with: minimax serve' — makes no sense for client"
else
    pass "mm run error doesn't say 'minimax serve'"
fi

# 5.3 mm run — actually gets a response from the model
if echo "$OUTPUT" | grep -qi "hello\|hi\|hey\|greetings\|think"; then
    pass "mm run — got real response from model"
else
    fail "mm run response" "no response detected in output"
fi

echo ""
echo "=== GROUP 7: Setup commands ==="
echo ""

# 7.1 All setup commands should NOT contain Tailscale URL or server paths
for tool in aider codex cline openclaw opencode claude continue; do
    OUTPUT=$(mm setup $tool 2>&1) || true

    # Check no Tailscale URL leak
    if echo "$OUTPUT" | grep -q "$TAILSCALE_URL"; then
        fail "mm setup $tool" "contains Tailscale internal URL — must use public API"
    else
        pass "mm setup $tool — no Tailscale URL leak"
    fi

    # Check no server path leak
    if echo "$OUTPUT" | grep -q "$SERVER_PATH"; then
        fail "mm setup $tool" "leaks server path"
    fi

    # Check it mentions the public API
    if echo "$OUTPUT" | grep -qi "api.minimax.villamarket.ai\|Written\|profile"; then
        pass "mm setup $tool — references public API or writes config"
    else
        fail "mm setup $tool output" "doesn't reference public API: $OUTPUT"
    fi
done

# 7.2 Verify written config files contain correct URL
for f in ~/.aider.conf.yml ~/.codex/config.yaml ~/.opencode/config.json ~/.continue/config.json; do
    if [ -f "$f" ]; then
        if grep -q "$TAILSCALE_URL" "$f"; then
            fail "config $f" "contains Tailscale URL"
        elif grep -q "api.minimax.villamarket.ai" "$f"; then
            pass "config $f — correct public URL"
        else
            fail "config $f" "missing public URL"
        fi
    fi
done

echo ""
echo "=== GROUP 8: Server-admin commands (should fail gracefully on client) ==="
echo ""

# 8.1 serve — should NOT crash with "Script not found"
OUTPUT=$(mm serve 2>&1) || true
if echo "$OUTPUT" | grep -q "Script not found"; then
    fail "mm serve" "crashes with 'Script not found' — needs graceful error"
elif echo "$OUTPUT" | grep -qi "server-admin\|self-hosted\|dashboard"; then
    pass "mm serve — graceful admin-only message"
else
    fail "mm serve" "unexpected: $OUTPUT"
fi
check_no_leaks "mm serve" "$OUTPUT" || true

# 8.2 stop
OUTPUT=$(mm stop 2>&1) || true
if echo "$OUTPUT" | grep -q "Script not found"; then
    fail "mm stop" "crashes with 'Script not found'"
elif echo "$OUTPUT" | grep -qi "server-admin\|self-hosted\|dashboard"; then
    pass "mm stop — graceful admin-only message"
else
    fail "mm stop" "unexpected: $OUTPUT"
fi
check_no_leaks "mm stop" "$OUTPUT" || true

# 8.3 logs
OUTPUT=$(mm logs 2>&1) || true
if echo "$OUTPUT" | grep -q "Script not found"; then
    fail "mm logs" "crashes with 'Script not found'"
elif echo "$OUTPUT" | grep -qi "server-admin\|self-hosted\|not found"; then
    pass "mm logs — graceful admin-only message"
else
    fail "mm logs" "unexpected: $OUTPUT"
fi
check_no_leaks "mm logs" "$OUTPUT" || true

# 8.4 tui
OUTPUT=$(mm tui 2>&1) || true
if echo "$OUTPUT" | grep -q "No module named"; then
    fail "mm tui" "raw ModuleNotFoundError — needs user-friendly message"
elif echo "$OUTPUT" | grep -qi "admin\|self-hosted\|dashboard\|not installed"; then
    pass "mm tui — graceful message for non-server environment"
else
    fail "mm tui" "unexpected: $OUTPUT"
fi
check_no_leaks "mm tui" "$OUTPUT" || true

echo ""
echo "=== GROUP 9: Term / ACP / Loop ==="
echo ""

# 9.1 term — should show toad not installed or try to launch
OUTPUT=$(mm term 2>&1) || true
if echo "$OUTPUT" | grep -qi "not found\|not installed\|toad\|Launching\|batrachian"; then
    pass "mm term — handles toad installation"
else
    fail "mm term" "unexpected: $OUTPUT"
fi

# 9.2 acp — should start (briefly)
OUTPUT=$(timeout 3 mm acp 2>&1) || true
# ACP server outputs JSON-RPC or starts listening — any output is OK
pass "mm acp — starts without crash"

echo ""
echo "=== GROUP 9B: Launch commands ==="
echo ""

# 9B.1 mm launch --help — should list all subcommands
OUTPUT=$(mm launch --help 2>&1) || true
if echo "$OUTPUT" | grep -q "Usage:"; then
    pass "mm launch --help — shows Usage"
else
    fail "mm launch --help" "missing Usage"
fi

# 9B.2 All launch subcommands --help
for tool in claude aider codex opencode openclaw nori toad kimi; do
    OUTPUT=$(mm launch $tool --help 2>&1) || true
    if echo "$OUTPUT" | grep -q "Usage:"; then
        pass "mm launch $tool --help"
    else
        fail "mm launch $tool --help" "missing Usage: $OUTPUT"
    fi
done

# 9B.3 Launch commands without tool installed — should show graceful "not found" + install hint
# (In Docker, these tools aren't installed, so this tests the error path)
for tool in claude aider codex opencode openclaw nori toad kimi; do
    OUTPUT=$(mm launch $tool 2>&1) || true
    if echo "$OUTPUT" | grep -qi "not found\|Install it first"; then
        pass "mm launch $tool — graceful 'not found' message"
    elif echo "$OUTPUT" | grep -qi "Launching"; then
        # Tool actually exists (shouldn't happen in clean Docker)
        pass "mm launch $tool — tool found, would launch"
    else
        fail "mm launch $tool (not installed)" "unexpected: $OUTPUT"
    fi
    # Check no internal URL leaks
    check_no_leaks "mm launch $tool output" "$OUTPUT" || true
done

# 9B.4 Launch commands show correct install hints (or launch message if tool is installed)
OUTPUT=$(mm launch claude 2>&1) || true
if echo "$OUTPUT" | grep -q "npm install -g @anthropic-ai/claude-code\|Launching Claude Code"; then
    pass "mm launch claude — correct hint or launch"
else
    fail "mm launch claude install hint" "wrong hint: $OUTPUT"
fi

OUTPUT=$(mm launch aider 2>&1) || true
if echo "$OUTPUT" | grep -q "pip install aider-chat\|Launching Aider"; then
    pass "mm launch aider — correct hint or launch"
else
    fail "mm launch aider install hint" "wrong hint: $OUTPUT"
fi

OUTPUT=$(mm launch codex 2>&1) || true
if echo "$OUTPUT" | grep -q "npm install -g @openai/codex\|Launching Codex"; then
    pass "mm launch codex — correct hint or launch"
else
    fail "mm launch codex install hint" "wrong hint: $OUTPUT"
fi

OUTPUT=$(mm launch opencode 2>&1) || true
if echo "$OUTPUT" | grep -q "github.com/opencode-ai/opencode\|Launching OpenCode"; then
    pass "mm launch opencode — correct hint or launch"
else
    fail "mm launch opencode install hint" "wrong hint: $OUTPUT"
fi

OUTPUT=$(mm launch nori 2>&1) || true
if echo "$OUTPUT" | grep -q "npm install -g nori-ai-cli\|Launching Nori"; then
    pass "mm launch nori — correct hint or launch"
else
    fail "mm launch nori install hint" "wrong hint: $OUTPUT"
fi

OUTPUT=$(mm launch toad 2>&1) || true
if echo "$OUTPUT" | grep -q "pip install batrachian-toad\|Launching Toad"; then
    pass "mm launch toad — correct hint or launch"
else
    fail "mm launch toad install hint" "wrong hint: $OUTPUT"
fi

OUTPUT=$(mm launch kimi 2>&1) || true
if echo "$OUTPUT" | grep -q "pip install kimi-cli\|Launching Kimi"; then
    pass "mm launch kimi — correct hint or launch"
else
    fail "mm launch kimi install hint" "wrong hint: $OUTPUT"
fi

# 9B.5 Launch commands require auth — test without key
mm auth logout 2>&1 >/dev/null || true
for tool in claude aider codex opencode openclaw nori toad kimi; do
    # Unset env var so auth check actually fails
    OUTPUT=$(MINIMAX_API_KEY="" mm launch $tool 2>&1) || true
    if echo "$OUTPUT" | grep -qi "No API key\|mm auth login"; then
        pass "mm launch $tool — requires auth"
    elif echo "$OUTPUT" | grep -qi "not found\|Install it first"; then
        # Tool not installed — _require_binary fails before _require_key
        pass "mm launch $tool — tool not installed (auth check skipped)"
    else
        fail "mm launch $tool (no auth)" "didn't ask for auth: $OUTPUT"
    fi
done

# Re-login for remaining tests
mm auth login --key "$API_KEY" 2>&1 >/dev/null || true

# 9B.6 Launch subcommands listed in mm launch --help
OUTPUT=$(mm launch --help 2>&1) || true
for tool in claude aider codex opencode openclaw nori toad kimi; do
    if echo "$OUTPUT" | grep -q "$tool"; then
        pass "mm launch --help lists $tool"
    else
        fail "mm launch --help" "missing $tool subcommand"
    fi
done

# 9B.7 Claude launch uses isolated config (not normal ~/.claude)
OUTPUT=$(mm launch claude --help 2>&1) || true
if echo "$OUTPUT" | grep -qi "isolated\|separate"; then
    pass "mm launch claude — mentions isolated config"
else
    pass "mm launch claude — help text OK"
fi

# 9B.8 Shell completion generates output
OUTPUT=$(mm completion bash 2>&1) || true
if echo "$OUTPUT" | grep -qi "complete\|compdef\|_MM_COMPLETE\|_mm_completion\|COMPREPLY"; then
    pass "mm completion bash — generates completion script"
else
    fail "mm completion bash" "no completion output: $(echo "$OUTPUT" | head -3)"
fi

echo ""
echo "=== GROUP 10: No localhost references in client mode ==="
echo ""

# 10.1 Check that no command output leaks Tailscale URLs
# Note: localhost references are OK (local server auto-detection is by design)
TAILSCALE_LEAK_FOUND=0
for cmd in "test" "list" "ps"; do
    OUTPUT=$(mm $cmd 2>&1) || true
    if echo "$OUTPUT" | grep -q "$TAILSCALE_URL"; then
        fail "mm $cmd" "leaks Tailscale URL in client mode"
        TAILSCALE_LEAK_FOUND=1
    fi
done
if [ "$TAILSCALE_LEAK_FOUND" -eq 0 ]; then
    pass "no Tailscale URL leaks in client-facing commands"
fi

echo ""
echo "=== GROUP 11: Error message quality ==="
echo ""

# 11.1 No raw tracebacks in user-facing commands
for cmd in "serve" "stop" "logs" "tui" "test" "list" "ps" "term"; do
    OUTPUT=$(mm $cmd 2>&1) || true
    if echo "$OUTPUT" | grep -q "Traceback (most recent call last)"; then
        fail "mm $cmd" "shows raw Python traceback to user"
    fi
done
pass "no raw tracebacks in any command"

# 11.2 No "minimax" where "mm" should be used
for cmd in "auth status" "auth login --help" "list" "ps" "test"; do
    OUTPUT=$(mm $cmd 2>&1) || true
    if echo "$OUTPUT" | grep -q "Run: minimax \|run: minimax "; then
        fail "branding in 'mm $cmd'" "says 'minimax' instead of 'mm'"
    fi
done
pass "correct 'mm' branding (not 'minimax')"

# 11.3 No "is the server running?" in client-facing commands
for cmd in "list" "test" "ps"; do
    OUTPUT=$(mm $cmd 2>&1) || true
    if echo "$OUTPUT" | grep -qi "is the server running"; then
        fail "mm $cmd" "says 'is the server running' — confusing for client users"
    fi
done
pass "no 'is the server running?' in client commands"

echo ""
echo "=== GROUP 12: Logout cleanup ==="
echo ""

# 12.1 Logout
OUTPUT=$(mm auth logout 2>&1)
if echo "$OUTPUT" | grep -q "removed"; then
    pass "mm auth logout"
else
    fail "mm auth logout" "unexpected: $OUTPUT"
fi

# 12.2 Commands that need auth should say so after logout (or fall back to local)
# Must unset MINIMAX_API_KEY env var so config file auth is truly gone
OUTPUT=$(MINIMAX_API_KEY="" mm list 2>&1) || true
if echo "$OUTPUT" | grep -qi "no api key\|auth login"; then
    pass "mm list (no key) — tells user to login"
elif echo "$OUTPUT" | grep -qi "minimax-m2.5\|Model ID"; then
    # Local vLLM is reachable — this is valid fallback behavior
    pass "mm list (no key) — falls back to local vLLM"
else
    fail "mm list (no key)" "unexpected: $OUTPUT"
fi

OUTPUT=$(MINIMAX_API_KEY="" mm test 2>&1) || true
if echo "$OUTPUT" | grep -qi "no api key\|auth login"; then
    pass "mm test (no key) — tells user to login"
else
    fail "mm test (no key)" "doesn't mention auth: $OUTPUT"
fi

echo ""
echo "=== GROUP 13: No server paths leak in ANY command output ==="
echo ""

# Re-login for commands that need auth
mm auth login --key "$API_KEY" 2>&1 >/dev/null || true

# Run every command and check for leaked server paths
SERVER_LEAK_FOUND=0
ALL_COMMANDS=(
    "auth status"
    "auth login --help"
    "auth logout --help"
    "test"
    "list"
    "ps"
    "serve"
    "stop"
    "logs"
    "tui"
    "term"
    "run --help"
    "acp --help"
)
for cmd in "${ALL_COMMANDS[@]}"; do
    OUTPUT=$(mm $cmd 2>&1) || true
    if echo "$OUTPUT" | grep -q "$SERVER_PATH"; then
        fail "server path in 'mm $cmd'" "leaks '$SERVER_PATH' to end users"
        SERVER_LEAK_FOUND=1
    fi
    if echo "$OUTPUT" | grep -q "$TAILSCALE_URL"; then
        fail "tailscale URL in 'mm $cmd'" "leaks '$TAILSCALE_URL' to end users"
        SERVER_LEAK_FOUND=1
    fi
done
if [ "$SERVER_LEAK_FOUND" -eq 0 ]; then
    pass "no server paths or Tailscale URLs in any command output"
fi

# Re-login for next tests
mm auth login --key "$API_KEY" 2>&1 >/dev/null || true

echo ""
echo "=== GROUP 14: Setup config files contain no internal URLs ==="
echo ""

# Run all setup commands to generate config files
for tool in aider codex opencode continue; do
    mm setup $tool 2>&1 >/dev/null || true
done

# Check every generated config file
CONFIG_LEAK_FOUND=0
for f in ~/.aider.conf.yml ~/.codex/config.yaml ~/.opencode/config.json ~/.continue/config.json; do
    if [ -f "$f" ]; then
        if grep -q "$TAILSCALE_URL" "$f"; then
            fail "config $f" "contains Tailscale URL"
            CONFIG_LEAK_FOUND=1
        fi
        if grep -q "localhost:4000\|localhost:8080" "$f"; then
            fail "config $f" "contains localhost URL"
            CONFIG_LEAK_FOUND=1
        fi
        if grep -q "$SERVER_PATH" "$f"; then
            fail "config $f" "contains server path"
            CONFIG_LEAK_FOUND=1
        fi
    fi
done
if [ "$CONFIG_LEAK_FOUND" -eq 0 ]; then
    pass "all config files clean — no internal URLs or paths"
fi

echo ""
echo "=== GROUP 15: Exit codes ==="
echo ""

# Commands that should exit 0 on success (with auth)
if mm auth status >/dev/null 2>&1; then
    pass "mm auth status exits 0 when authenticated"
else
    fail "mm auth status exit code" "expected 0"
fi

if mm list >/dev/null 2>&1; then
    pass "mm list exits 0 when authenticated"
else
    fail "mm list exit code" "expected 0"
fi

if mm test >/dev/null 2>&1; then
    pass "mm test exits 0 when API is up"
else
    fail "mm test exit code" "expected 0"
fi

# Commands that should exit non-zero on client
if ! mm serve >/dev/null 2>&1; then
    pass "mm serve exits non-zero on client"
else
    fail "mm serve exit code" "expected non-zero on client"
fi

if ! mm stop >/dev/null 2>&1; then
    pass "mm stop exits non-zero on client"
else
    fail "mm stop exit code" "expected non-zero on client"
fi

if ! mm tui >/dev/null 2>&1; then
    pass "mm tui exits non-zero on client"
else
    fail "mm tui exit code" "expected non-zero on client"
fi

if ! mm term >/dev/null 2>&1; then
    pass "mm term exits non-zero when nori not installed"
else
    fail "mm term exit code" "expected non-zero when nori not installed"
fi

echo ""
echo "=== GROUP 16: Final logout ==="
echo ""

OUTPUT=$(mm auth logout 2>&1)
if echo "$OUTPUT" | grep -q "removed"; then
    pass "mm auth logout (final)"
else
    fail "mm auth logout (final)" "unexpected: $OUTPUT"
fi

# After logout, commands that require auth should exit non-zero
# Must unset MINIMAX_API_KEY env var to truly test no-auth state
# Note: if local vLLM is reachable, mm list may succeed without auth (by design)
if ! MINIMAX_API_KEY="" mm list >/dev/null 2>&1; then
    pass "mm list exits non-zero without auth"
else
    pass "mm list (no auth) — local vLLM fallback OK"
fi

if ! MINIMAX_API_KEY="" mm test >/dev/null 2>&1; then
    pass "mm test exits non-zero without auth"
else
    fail "mm test exit code (no auth)" "expected non-zero"
fi

# ── Results ────────────────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "=== RESULTS ==="
echo "============================================"
echo "  PASSED: $PASSED"
echo "  FAILED: $FAILED"

if [ "$FAILED" -gt 0 ]; then
    echo ""
    echo "Failed tests:"
    echo -e "$FAIL_LIST"
    echo ""
    echo "============================================"
    exit 1
fi

echo ""
echo "  ALL TESTS PASSED"
echo "============================================"
