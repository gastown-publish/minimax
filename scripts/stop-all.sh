#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LITELLM_PID_FILE="/tmp/litellm-minimax.pid"

echo "=== Stopping MiniMax-M2.5 Full Stack ==="
echo ""

# Step 1: Stop LiteLLM
echo "--- Stopping LiteLLM proxy ---"
if [ -f "$LITELLM_PID_FILE" ]; then
    PID=$(cat "$LITELLM_PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        sleep 3
        kill -9 "$PID" 2>/dev/null
        echo "LiteLLM stopped (PID $PID)."
    else
        echo "LiteLLM PID $PID not running."
    fi
    rm -f "$LITELLM_PID_FILE"
else
    PIDS=$(pgrep -f "litellm.*minimax" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        kill $PIDS 2>/dev/null
        sleep 3
        kill -9 $PIDS 2>/dev/null
        echo "LiteLLM stopped."
    else
        echo "No LiteLLM process found."
    fi
fi

echo ""

# Step 2: Stop vLLM
echo "--- Stopping vLLM server ---"
"$SCRIPT_DIR/stop.sh"

echo ""
echo "=== Full stack stopped ==="
