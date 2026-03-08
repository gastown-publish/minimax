#!/bin/bash
set -e

VENV="/home/nic/data/models/MiniMax-M2.5/.venv"
MODEL="/home/nic/data/models/MiniMax-M2.5-HF"
LOG="/tmp/vllm-minimax.log"
PID_FILE="/tmp/vllm-minimax.pid"
PORT=8080

# Clear any stale CUDA compat paths (driver 590+ provides native support)
unset LD_PRELOAD
export LD_LIBRARY_PATH=""

# Use CUDA 12.8 toolkit (system default nvcc is 12.0 which breaks FP8 block scaling in flashinfer)
export CUDA_HOME=/usr/local/cuda-12.8

# Check venv
if [ ! -f "$VENV/bin/vllm" ]; then
    echo "ERROR: vLLM not found. Run: $VENV/bin/pip install vllm"
    exit 1
fi

# Check model
if [ ! -f "$MODEL/config.json" ]; then
    echo "ERROR: Model not found at $MODEL"
    echo "Download it: ./scripts/download-model.sh"
    exit 1
fi

# Check port
if ss -tlnp | grep -q ":${PORT} "; then
    echo "ERROR: Port $PORT is already in use"
    ss -tlnp | grep ":${PORT} "
    exit 1
fi

echo "Starting vLLM server on port $PORT..."
echo "Model: MiniMax-M2.5 (FP8, ~230 GB)"
echo "Log: $LOG"
echo "GPUs: 8x H100 (tensor parallel + expert parallel)"

# Disable custom all-reduce (CUDA IPC fails in LXC container)
export VLLM_DISABLE_CUSTOM_ALL_REDUCE=1
export SAFETENSORS_FAST_GPU=1

nohup "$VENV/bin/vllm" serve "$MODEL" \
    --host 0.0.0.0 \
    --port "$PORT" \
    --tensor-parallel-size 8 \
    --enable-expert-parallel \
    --trust-remote-code \
    --gpu-memory-utilization 0.95 \
    --max-num-seqs 16 \
    --max-model-len 131072 \
    --enable-prefix-caching \
    --enable-chunked-prefill \
    --enable-auto-tool-choice \
    --tool-call-parser minimax_m2 \
    --reasoning-parser minimax_m2_append_think \
    --served-model-name minimax-m2.5 MiniMaxAI/MiniMax-M2.5 \
    --compilation-config '{"cudagraph_mode": "PIECEWISE"}' \
    > "$LOG" 2>&1 &

PID=$!
echo "$PID" > "$PID_FILE"
echo "Server PID: $PID"

echo "Waiting for model to load (FP8 loads faster than INT4, ~10-20 minutes)..."
for i in $(seq 1 480); do
    sleep 5
    if ! kill -0 "$PID" 2>/dev/null; then
        echo "ERROR: vLLM process died. Check log: tail -50 $LOG"
        tail -20 "$LOG"
        exit 1
    fi
    HEALTH=$(curl -s http://localhost:${PORT}/health 2>/dev/null || echo "")
    if [ "$HEALTH" = "" ]; then
        :
    elif echo "$HEALTH" | grep -q "ok\|200\|healthy"; then
        echo "Model loaded and ready!"
        echo "API: http://localhost:${PORT}/v1"
        exit 0
    fi
    # Show progress every 30s
    if [ $((i % 6)) -eq 0 ]; then
        VRAM=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | awk '{s+=$1} END {printf "%.0f", s}')
        echo "  Loading... (${VRAM} MiB VRAM used, ${i}x5s elapsed)"
    fi
done

echo "WARNING: Model did not finish loading within 40 minutes."
echo "Check log: tail -f $LOG"
