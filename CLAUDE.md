# CLAUDE.md — AI Agent Instructions

This repo manages a local MiniMax-M2.5 deployment on an 8x H100 80GB GPU server.

## What This Is

MiniMax-M2.5 served via vLLM with tensor parallel + expert parallel across 8 GPUs.
The model ships as native FP8 weights (~230 GB), fitting comfortably with ~375 GB left for KV cache.
This enables 128K context per request — ideal for coding workloads.

The server exposes an OpenAI-compatible API on port 8080. LiteLLM (port 4000) handles API key management, cost tracking, and proxying.

## Key Paths

- **Model weights**: `/home/nic/data/models/MiniMax-M2.5-HF/` (~230 GB, 126 safetensors shards, FP8)
- **vLLM venv**: `/home/nic/data/models/MiniMax-M2.5/.venv/` (Python 3.12, vLLM + LiteLLM)
- **vLLM log**: `/tmp/vllm-minimax.log`
- **LiteLLM log**: `/tmp/litellm-minimax.log`
- **LiteLLM config**: `./litellm-config.yaml`
- **TUI admin**: `./admin` (or `minimax-admin` if symlinked)

## Important Warnings

- The model uses ~230 GB VRAM across 8 GPUs. With 128K context and KV cache, total usage can reach ~600 GB.
- There is NO authentication on port 8080. LiteLLM (port 4000) handles API key auth.
- CUDA only works because the LXC host was configured for GPU passthrough. If `cuInit()` returns error 802, the host admin needs to fix GPU passthrough again.
- **CRITICAL**: Must set `LD_LIBRARY_PATH=""` before running vLLM. The cuda-compat path in `/etc/environment` breaks CUDA init. The start scripts handle this automatically.
- **CRITICAL**: Must set `CUDA_HOME=/usr/local/cuda-12.8` — the system default nvcc is 12.0 (`nvidia-cuda-toolkit` package) which causes flashinfer to reject FP8 block scaling. CUDA 12.8+ is required.
- **CRITICAL**: Must use `--enable-expert-parallel` — pure TP8 is not supported for MoE routing on this model.

## Common Tasks

### Check if server is running
```bash
./scripts/health.sh
```

### Start full stack (vLLM + LiteLLM)
```bash
./scripts/start-all.sh
```

### Start vLLM only
```bash
./scripts/start.sh
```

### Stop everything
```bash
./scripts/stop-all.sh
```

### Test inference
```bash
./scripts/test.sh
```

### Admin TUI
```bash
./admin
```

### Download model
```bash
./scripts/download-model.sh
```

## Server Parameters

```
vllm serve /home/nic/data/models/MiniMax-M2.5-HF
    --tensor-parallel-size 8
    --enable-expert-parallel         (required for MoE routing)
    --gpu-memory-utilization 0.95
    --max-model-len 131072           (128K context)
    --max-num-seqs 16
    --enable-prefix-caching          (reuse system prompt KV cache)
    --enable-chunked-prefill
    --enable-auto-tool-choice
    --tool-call-parser minimax_m2    (function calling)
    --reasoning-parser minimax_m2_append_think  (separates <think> blocks)
    --compilation-config '{"cudagraph_mode": "PIECEWISE"}'
```

## Model Info

- **Name**: MiniMax-M2.5
- **Source**: MiniMaxAI/MiniMax-M2.5
- **Precision**: FP8 (native)
- **Size**: ~230 GB
- **Architecture**: MoE (Mixture of Experts)
- **Context**: 128K tokens
- **Benchmarks**: 80.2% SWE-Bench Verified, 51.3% Multi-SWE-Bench

## Pricing (LiteLLM cost tracking)

- Input: $0.30 / 1M tokens
- Output: $1.20 / 1M tokens

## Infrastructure

- **Caddy** (port 8090): Reverse proxy to LiteLLM on 4000
- **PostgreSQL**: localhost:5432, database `litellm`
- **Tailscale**: Public endpoint via Funnel
- **NVIDIA driver**: 590.48.01 required

## Performance Baseline

- FP8 loads faster than INT4 (~10-20 minutes vs 30-40)
- Expert parallel enables full 128K context
- Prefix caching significantly speeds up repeated system prompts
