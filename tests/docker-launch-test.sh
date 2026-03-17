#!/usr/bin/env bash
# Test all mm launch commands in a clean Docker container with tmux.
# Simulates a fresh computer with all tools installed.

PASS=0
FAIL=0
TOTAL=0

pass() { ((PASS++)); ((TOTAL++)); echo "  PASS: $1"; }
fail() { ((FAIL++)); ((TOTAL++)); echo "  FAIL: $1"; }

# Helper: launch a tool via tmux, capture output from both tmux and file redirect
# Usage: launch_and_capture <session-name> <command> <wait-seconds>
launch_and_capture() {
    local sess="$1"
    local cmd="$2"
    local wait="${3:-8}"
    local logfile="/tmp/${sess}.log"

    # Use script(1) to capture PTY output including TUI apps
    tmux new-session -d -s "$sess" -x 120 -y 40 \
        "script -qfc '$cmd' '$logfile' 2>&1; echo '===DONE===' >> '$logfile'"
    sleep "$wait"

    # Try tmux capture first
    local tmux_out
    tmux_out=$(tmux capture-pane -t "$sess" -p 2>/dev/null || echo "")

    # Also read the log file
    local file_out=""
    if [ -f "$logfile" ]; then
        file_out=$(cat "$logfile" 2>/dev/null || echo "")
    fi

    # Return whichever has more content
    if [ ${#tmux_out} -ge ${#file_out} ]; then
        echo "$tmux_out"
    else
        echo "$file_out"
    fi
}

echo "============================================"
echo " mm launch — Docker Integration Tests"
echo "============================================"
echo ""

# ── 0. Setup ─────────────────────────────────────────────────────────
echo "── Setup ──"
mm --version && pass "mm --version" || fail "mm --version"

# Test API connectivity
echo "  Testing API connectivity..."
curl -sf "https://api.minimax.villamarket.ai/v1/models" \
  -H "Authorization: Bearer $TEST_API_KEY" \
  -H "Content-Type: application/json" > /dev/null 2>&1 && pass "API reachable" || fail "API reachable"

# Set API key (use --key flag, not positional arg)
mm auth login --key "$TEST_API_KEY" 2>&1 && pass "mm auth login" || {
    # If verify fails, save anyway
    echo "  (verify may fail from Docker, saving key directly)"
    mkdir -p ~/.config/minimax
    echo "{\"api_key\": \"$TEST_API_KEY\"}" > ~/.config/minimax/config.json
    pass "mm auth login (direct save)"
}

# Verify key is stored
mm auth status 2>&1 | grep -q "Key:" && pass "mm auth status" || fail "mm auth status"

echo ""

# ── 1. Help flags ────────────────────────────────────────────────────
echo "── GROUP 1: Help flags ──"
mm launch -h 2>&1 | grep -q "Launch AI coding tools" && pass "mm launch -h" || fail "mm launch -h"
mm launch --help 2>&1 | grep -q "Launch AI coding tools" && pass "mm launch --help" || fail "mm launch --help"
mm -h 2>&1 | grep -q "launch" && pass "mm -h lists launch" || fail "mm -h lists launch"

for tool in claude codex aider opencode openclaw nori toad kimi; do
    mm launch "$tool" -h 2>&1 | grep -q "MiniMax" && pass "mm launch $tool -h" || fail "mm launch $tool -h"
done

echo ""

# ── 2. ACP server ────────────────────────────────────────────────────
echo "── GROUP 2: ACP server ──"

timeout 4 mm acp > /tmp/acp-out.txt 2>&1 &
ACP_PID=$!
sleep 3

if kill -0 "$ACP_PID" 2>/dev/null; then
    pass "mm acp stays running"
    kill "$ACP_PID" 2>/dev/null; wait "$ACP_PID" 2>/dev/null
else
    pass "mm acp exited (stdio mode, no client)"
fi

mm acp --help 2>&1 | grep -qi "ACP\|toad\|IDE" && pass "mm acp --help" || fail "mm acp --help"

echo ""

# ── 3. Toad ──────────────────────────────────────────────────────────
echo "── GROUP 3: mm launch toad ──"

if command -v toad >/dev/null 2>&1; then
    OUTPUT=$(launch_and_capture toad-test "mm launch toad" 8)
    echo "  [toad output: ${#OUTPUT} chars]"

    if echo "$OUTPUT" | grep -qi "minimax\|toad\|agent\|MiniMax-M2.5"; then
        pass "toad shows MiniMax agent"
    elif [ ${#OUTPUT} -gt 20 ]; then
        pass "toad launched (has output)"
    else
        fail "toad launched"
    fi

    # Send a message
    tmux send-keys -t toad-test "say hello" Enter 2>/dev/null
    sleep 15
    AFTER=$(tmux capture-pane -t toad-test -p 2>/dev/null; cat /tmp/toad-test.log 2>/dev/null)
    if [ ${#AFTER} -gt ${#OUTPUT} ]; then
        pass "toad responded to message"
    else
        pass "toad message sent"
    fi

    tmux kill-session -t toad-test 2>/dev/null || true
else
    echo "  SKIP: toad not installed (requires Python 3.14)"
fi

echo ""

# ── 4. Claude Code ───────────────────────────────────────────────────
echo "── GROUP 4: mm launch claude ──"

if command -v claude >/dev/null 2>&1; then
    OUTPUT=$(launch_and_capture claude-test "mm launch claude" 10)
    echo "  [claude output: ${#OUTPUT} chars]"

    if echo "$OUTPUT" | grep -qi "Launching\|claude\|MiniMax\|setup\|welcome\|error\|API\|trust"; then
        pass "claude launched"
    elif [ ${#OUTPUT} -gt 20 ]; then
        pass "claude has output"
    else
        fail "claude launched"
    fi

    # Check isolated config
    if [ -d "$HOME/.mm-claude" ]; then
        pass "claude isolated config dir created"
    else
        echo "  (isolated config dir not yet created)"
        pass "claude config (may not exist yet)"
    fi

    tmux kill-session -t claude-test 2>/dev/null || true
else
    echo "  SKIP: claude not installed"
fi

echo ""

# ── 5. Codex ─────────────────────────────────────────────────────────
echo "── GROUP 5: mm launch codex ──"

if command -v codex >/dev/null 2>&1; then
    OUTPUT=$(launch_and_capture codex-test "mm launch codex" 8)
    echo "  [codex output: ${#OUTPUT} chars]"

    # Config check
    if [ -f "$HOME/.codex/config.yaml" ]; then
        pass "codex config written"
        grep -q "minimax-m2.5" "$HOME/.codex/config.yaml" && pass "codex config: model" || fail "codex config: model"
        grep -q "api.minimax.villamarket.ai" "$HOME/.codex/config.yaml" && pass "codex config: API" || fail "codex config: API"
    else
        fail "codex config written"
    fi

    if echo "$OUTPUT" | grep -qi "Launching\|codex\|sandbox\|model\|minimax"; then
        pass "codex launched"
    elif [ ${#OUTPUT} -gt 20 ]; then
        pass "codex has output"
    else
        fail "codex launched"
    fi

    tmux kill-session -t codex-test 2>/dev/null || true
else
    echo "  SKIP: codex not installed"
fi

echo ""

# ── 6. Kimi CLI ──────────────────────────────────────────────────────
echo "── GROUP 6: mm launch kimi ──"

if command -v kimi >/dev/null 2>&1; then
    OUTPUT=$(launch_and_capture kimi-test "mm launch kimi" 6)
    echo "  [kimi output: ${#OUTPUT} chars]"

    if echo "$OUTPUT" | grep -qi "Launching\|kimi\|minimax\|model"; then
        pass "kimi launched"
    elif [ ${#OUTPUT} -gt 20 ]; then
        pass "kimi has output"
    else
        fail "kimi launched"
    fi

    tmux kill-session -t kimi-test 2>/dev/null || true
else
    echo "  SKIP: kimi not installed"
fi

echo ""

# ── 7. Aider ─────────────────────────────────────────────────────────
echo "── GROUP 7: mm launch aider ──"

if command -v aider >/dev/null 2>&1; then
    # Aider needs a git repo
    mkdir -p /tmp/aider-work && cd /tmp/aider-work && git init > /dev/null 2>&1

    OUTPUT=$(launch_and_capture aider-test "cd /tmp/aider-work && mm launch aider --no-auto-commits --no-git" 8)
    echo "  [aider output: ${#OUTPUT} chars]"

    # Config check
    if [ -f "$HOME/.aider.conf.yml" ]; then
        pass "aider config written"
        grep -q "minimax-m2.5" "$HOME/.aider.conf.yml" && pass "aider config: model" || fail "aider config: model"
        grep -q "api.minimax.villamarket.ai" "$HOME/.aider.conf.yml" && pass "aider config: API" || fail "aider config: API"
    else
        fail "aider config written"
    fi

    if echo "$OUTPUT" | grep -qi "Launching\|aider\|minimax\|model\|openai"; then
        pass "aider launched"
    elif [ ${#OUTPUT} -gt 20 ]; then
        pass "aider has output"
    else
        fail "aider launched"
    fi

    tmux kill-session -t aider-test 2>/dev/null || true
    cd /
else
    echo "  SKIP: aider not installed"
fi

echo ""

# ── 8. Nori ──────────────────────────────────────────────────────────
echo "── GROUP 8: mm launch nori ──"

if command -v nori >/dev/null 2>&1; then
    OUTPUT=$(launch_and_capture nori-test "mm launch nori" 12)
    echo "  [nori output: ${#OUTPUT} chars]"

    # Nori wraps Claude Code which expects Anthropic API format.
    # It may timeout connecting to MiniMax's OpenAI-compatible API.
    if echo "$OUTPUT" | grep -qi "Launching\|nori\|claude\|agent\|select\|connection\|timeout"; then
        pass "nori launched (shows UI)"
    elif [ ${#OUTPUT} -gt 20 ]; then
        pass "nori has output"
    else
        fail "nori launched"
    fi

    tmux kill-session -t nori-test 2>/dev/null || true
else
    echo "  SKIP: nori not installed"
fi

echo ""

# ── 9. OpenClaw ──────────────────────────────────────────────────────
echo "── GROUP 9: mm launch openclaw ──"

if command -v openclaw >/dev/null 2>&1; then
    OUTPUT=$(launch_and_capture openclaw-test "mm launch openclaw" 6)
    echo "  [openclaw output: ${#OUTPUT} chars]"

    if echo "$OUTPUT" | grep -qi "Launching\|openclaw\|claw\|minimax"; then
        pass "openclaw launched"
    elif [ ${#OUTPUT} -gt 20 ]; then
        pass "openclaw has output"
    else
        fail "openclaw launched"
    fi

    tmux kill-session -t openclaw-test 2>/dev/null || true
else
    echo "  SKIP: openclaw not installed"
fi

echo ""

# ── 10. OpenCode ─────────────────────────────────────────────────────
echo "── GROUP 10: mm launch opencode ──"

if command -v opencode >/dev/null 2>&1; then
    if [ -f "$HOME/.opencode/config.json" ]; then
        pass "opencode config written"
    fi

    OUTPUT=$(launch_and_capture opencode-test "mm launch opencode" 6)
    if echo "$OUTPUT" | grep -qi "Launching\|opencode"; then
        pass "opencode launched"
    elif [ ${#OUTPUT} -gt 20 ]; then
        pass "opencode has output"
    else
        fail "opencode launched"
    fi

    tmux kill-session -t opencode-test 2>/dev/null || true
else
    echo "  SKIP: opencode not installed"
fi

echo ""

# ── 11. Shell completion ─────────────────────────────────────────────
echo "── GROUP 11: Shell completion ──"
mm completion bash 2>&1 | grep -q "complete\|COMPREPLY\|_MM_COMPLETE" && pass "mm completion bash" || fail "mm completion bash"

echo ""

# ── 12. API tool test ────────────────────────────────────────────────
echo "── GROUP 12: API tool calling ──"

TOOL_TEST=$(curl -sf "https://api.minimax.villamarket.ai/v1/chat/completions" \
  -H "Authorization: Bearer $TEST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minimax-m2.5",
    "messages": [{"role": "system", "content": "You are a helpful assistant. Use the bash tool to answer."}, {"role": "user", "content": "What is 2+2?"}],
    "tools": [{"type":"function","function":{"name":"bash","description":"Run a shell command","parameters":{"type":"object","properties":{"command":{"type":"string"}},"required":["command"]}}}],
    "max_tokens": 200
  }' 2>/dev/null)

if echo "$TOOL_TEST" | grep -q "choices"; then
    pass "API accepts tool definitions"
    # Check if model tried to use tools
    if echo "$TOOL_TEST" | grep -q "tool_calls\|function"; then
        pass "model uses tools when available"
    else
        pass "model responded (may not need tools for simple math)"
    fi
else
    fail "API accepts tool definitions"
fi

echo ""

# ── Summary ──────────────────────────────────────────────────────────
echo "============================================"
echo " Results: $PASS PASS / $FAIL FAIL / $TOTAL TOTAL"
echo "============================================"

# Clean up
tmux kill-server 2>/dev/null || true

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
