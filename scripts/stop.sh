#!/bin/bash

PID_FILE="/tmp/vllm-minimax.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping vLLM server (PID $PID)..."
        kill "$PID"
        sleep 5
        if kill -0 "$PID" 2>/dev/null; then
            echo "Force killing..."
            kill -9 "$PID" 2>/dev/null
            sleep 2
        fi
        echo "Stopped."
        rm -f "$PID_FILE"
        exit 0
    else
        echo "PID $PID is not running. Cleaning up stale PID file."
        rm -f "$PID_FILE"
    fi
fi

# Fallback: find by process name
PIDS=$(pgrep -f "vllm serve.*MiniMax" 2>/dev/null || true)
if [ -n "$PIDS" ]; then
    echo "Found vLLM processes: $PIDS"
    kill $PIDS 2>/dev/null
    sleep 5
    kill -9 $PIDS 2>/dev/null
    echo "Stopped."
else
    echo "No MiniMax vLLM server running."
fi
