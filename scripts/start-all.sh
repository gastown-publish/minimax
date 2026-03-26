#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV="/home/nic/data/models/MiniMax-M2.5/.venv"
LITELLM_CONFIG="$REPO_DIR/litellm-config.yaml"
LITELLM_LOG="/tmp/litellm-minimax.log"
LITELLM_PID_FILE="/tmp/litellm-minimax.pid"
LOCK_FILE="/tmp/litellm-minimax.lock"

echo "=== Starting MiniMax-M2.5 Full Stack ==="
echo ""

# Step 1: Start vLLM
echo "--- Step 1: Starting vLLM server ---"
"$SCRIPT_DIR/start.sh"
echo ""

# Step 2: Start LiteLLM
echo "--- Step 2: Starting LiteLLM proxy ---"

if [ ! -f "$LITELLM_CONFIG" ]; then
    echo "ERROR: LiteLLM config not found at $LITELLM_CONFIG"
    exit 1
fi

if ss -tlnp | grep -q ":4000 "; then
    echo "LiteLLM already running on port 4000"
else
    # Database connection for API key persistence
    export DATABASE_URL="postgresql://litellm:litellm-kimi-k25@localhost:5432/litellm"
    export LD_LIBRARY_PATH=""
    # Prisma binary must be on PATH for LiteLLM to connect to DB
    export PATH="$VENV/bin:$PATH"

    nohup "$VENV/bin/litellm" \
        --config "$LITELLM_CONFIG" \
        --host 0.0.0.0 \
        --port 4000 \
        > "$LITELLM_LOG" 2>&1 &

    LITELLM_PID=$!
    (flock -x 200; echo "$LITELLM_PID" > "$LITELLM_PID_FILE") 200>"$LOCK_FILE"
    echo "LiteLLM PID: $LITELLM_PID"
    echo "LiteLLM log: $LITELLM_LOG"

    # Wait for LiteLLM to be ready
    for i in $(seq 1 30); do
        sleep 2
        if curl -s http://localhost:4000/health 2>/dev/null | grep -q "healthy\|ok\|running"; then
            echo "LiteLLM proxy ready on port 4000"
            break
        fi
        if [ "$i" -eq 30 ]; then
            echo "WARNING: LiteLLM may not be ready yet. Check: tail -f $LITELLM_LOG"
        fi
    done
fi

echo ""
echo "=== Full stack is running ==="
echo "  vLLM:    http://localhost:8080/v1  (direct, no auth)"
echo "  LiteLLM: http://localhost:4000/v1  (proxy, API key required)"
echo "  Caddy:   http://localhost:8090     (external proxy)"
