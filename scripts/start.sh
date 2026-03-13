#!/bin/bash
set -e

VENV="/home/nic/data/models/MiniMax-M2.5/.venv"
MODEL="/home/nic/data/models/MiniMax-M2.5-HF"
LOG="/tmp/vllm-minimax.log"
PID_FILE="/tmp/vllm-minimax.pid"
PORT=8080

# ── GPU Configuration ───────────────────────────────────────────────
# Default: 4 GPUs (TP4 + EP). Pass "8" to use all 8 GPUs (TP8 + EP).
NUM_GPUS="${1:-4}"

if [ "$NUM_GPUS" = "8" ]; then
    TP_SIZE=8
    MAX_SEQS=16
    unset CUDA_VISIBLE_DEVICES
    GPU_LABEL="8x H100 (TP=8 + EP)"
elif [ "$NUM_GPUS" = "4" ]; then
    TP_SIZE=4
    MAX_SEQS=16
    export CUDA_VISIBLE_DEVICES=0,1,2,3
    GPU_LABEL="4x H100 (TP=4 + EP) — GPUs 0-3, GPUs 4-7 free"
else
    echo "ERROR: Only 4 or 8 GPUs supported (KV heads=8, TP must divide evenly)"
    exit 1
fi

# ── Environment ─────────────────────────────────────────────────────
# Clear stale CUDA compat paths (driver 590+ provides native support)
unset LD_PRELOAD
export LD_LIBRARY_PATH=""

# CUDA 12.8 toolkit (system nvcc 12.0 breaks FP8 block scaling in flashinfer)
export CUDA_HOME=/usr/local/cuda-12.8

# Disable custom all-reduce (CUDA IPC fails in LXC container)
export VLLM_DISABLE_CUSTOM_ALL_REDUCE=1

# GPU-accelerated safetensors loading
export SAFETENSORS_FAST_GPU=1

# ── Performance Optimizations ───────────────────────────────────────
# DeepGEMM is faster for linear layers but SLOWER for MoE expert grouped GEMM.
# Disabling it for MoE uses Cutlass BlockScaled GroupedGemm instead: +57% throughput on H100.
# See: https://github.com/vllm-project/recipes/pull/120
export VLLM_MOE_USE_DEEP_GEMM=0

# ── Checks ──────────────────────────────────────────────────────────
if [ ! -f "$VENV/bin/vllm" ]; then
    echo "ERROR: vLLM not found. Run: $VENV/bin/pip install vllm"
    exit 1
fi

if [ ! -f "$MODEL/config.json" ]; then
    echo "ERROR: Model not found at $MODEL"
    echo "Download it: ./scripts/download-model.sh"
    exit 1
fi

if ss -tlnp | grep -q ":${PORT} "; then
    echo "ERROR: Port $PORT is already in use"
    ss -tlnp | grep ":${PORT} "
    exit 1
fi

# ── Launch ──────────────────────────────────────────────────────────
echo "Starting vLLM server on port $PORT..."
echo "Model: MiniMax-M2.5 (FP8, ~230 GB)"
echo "GPUs:  $GPU_LABEL"
echo "Config: TP=$TP_SIZE, max-seqs=$MAX_SEQS, ctx=128K, prefix-cache=on, CUDA-graphs=PIECEWISE"
echo "Optimizations: VLLM_MOE_USE_DEEP_GEMM=0"
echo "Log:   $LOG"

nohup "$VENV/bin/vllm" serve "$MODEL" \
    --host 0.0.0.0 \
    --port "$PORT" \
    --tensor-parallel-size "$TP_SIZE" \
    --enable-expert-parallel \
    --trust-remote-code \
    --gpu-memory-utilization 0.95 \
    --max-num-seqs "$MAX_SEQS" \
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

echo "Waiting for model to load (~10-20 minutes for FP8)..."
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
