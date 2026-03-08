#!/bin/bash
set -e

VENV="/home/nic/data/models/Kimi-K2.5-GGUF/.venv"
MODEL_DIR="/home/nic/data/models/MiniMax-M2.5-HF"

# Check venv
if [ ! -f "$VENV/bin/huggingface-cli" ]; then
    echo "ERROR: huggingface-cli not found. Run: $VENV/bin/pip install huggingface-hub hf_transfer"
    exit 1
fi

echo "=== Downloading MiniMax-M2.5 (FP8, ~230 GB) ==="
echo "Source: MiniMaxAI/MiniMax-M2.5"
echo "Destination: $MODEL_DIR"
echo ""

HF_HUB_ENABLE_HF_TRANSFER=1 "$VENV/bin/huggingface-cli" download \
    MiniMaxAI/MiniMax-M2.5 \
    --local-dir "$MODEL_DIR"

echo ""
echo "Download complete!"
echo "Size: $(du -sh "$MODEL_DIR" | cut -f1)"
echo "Shards: $(ls "$MODEL_DIR"/model-*.safetensors 2>/dev/null | wc -l)"
