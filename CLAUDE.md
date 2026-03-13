# CLAUDE.md — AI Agent Instructions

This repo manages the MiniMax-M2.5 platform: inference server, website, chat UI, CLI, and iOS app.

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │  minimax.villamarket.ai (Website)    │
                    │  S3 + CloudFront E2AFMAXJ9YXUTH     │
                    └─────────────────────────────────────┘
                    ┌─────────────────────────────────────┐
                    │  app.minimax.villamarket.ai (Chat)   │
                    │  CloudFront E7MNC26N70Y7Z            │
                    │  → Tailscale Funnel :10000           │
                    │  → DeerFlow (Docker)                 │
                    └───────────┬─────────────────────────┘
                                │
    ┌───────────────────────────▼──────────────────────────┐
    │               LiteLLM (port 4000)                    │
    │  API key auth, cost tracking, request routing        │
    └───────────────────────────┬──────────────────────────┘
                                │
    ┌───────────────────────────▼──────────────────────────┐
    │               vLLM (port 8080)                       │
    │  MiniMax-M2.5, TP8 + Expert Parallel, FP8            │
    │  8x H100 80GB, 128K context                          │
    └──────────────────────────────────────────────────────┘
```

## Key Paths

| Path | Description |
|------|-------------|
| `scripts/` | Server start/stop/health/test scripts |
| `src/minimax_cli/` | Ollama-style CLI (pip install -e .) |
| `tui/` | Admin TUI for API key management |
| `website/` | minimax.villamarket.ai (Next.js static export) |
| `website/src/` | Website source (pages, components, auth) |
| `website/lambda/` | AWS Lambda functions (keys, billing, promos) |
| `ios/` | Native iOS app (Swift, SwiftUI) |
| `litellm-config.yaml` | LiteLLM config (gitignored — has secrets) |
| `litellm-config.example.yaml` | Example LiteLLM config (safe to commit) |
| `admin` | Symlink to TUI launcher |

### External Paths (not in repo)

| Path | Description |
|------|-------------|
| `/home/nic/data/models/MiniMax-M2.5-HF/` | Model weights (~230 GB, FP8) |
| `/home/nic/data/deerflow/` | DeerFlow source (separate repo) |
| `.venv/` | Python venv (vLLM 0.17.0, LiteLLM 1.82.0) |

## Important Warnings

- **CRITICAL**: Must set `LD_LIBRARY_PATH=""` before running vLLM. cuda-compat in `/etc/environment` breaks CUDA init.
- **CRITICAL**: Must set `CUDA_HOME=/usr/local/cuda-12.8` — system nvcc is 12.0, flashinfer FP8 needs 12.8+.
- **CRITICAL**: Must use `--enable-expert-parallel` — pure TP8 not supported for MoE routing.
- **CRITICAL**: Must use `VLLM_DISABLE_CUSTOM_ALL_REDUCE=1` — CUDA IPC fails in LXC container.
- LiteLLM model `minimax-m2.5` must use `api_base: http://localhost:8080/v1` (direct vLLM), NOT CloudFront URLs.
- There is NO auth on port 8080. LiteLLM (port 4000) handles API key auth.

## Common Tasks

| Task | Command |
|------|---------|
| Start full stack | `./scripts/start-all.sh` |
| Start vLLM only | `./scripts/start.sh` |
| Stop everything | `./scripts/stop-all.sh` |
| Health check | `./scripts/health.sh` |
| Test inference | `./scripts/test.sh` |
| Admin TUI | `./admin` |
| Build + deploy website | `cd website && npm run build && ./deploy.sh` |

## Website

- **Stack**: Next.js 14, React, Tailwind, static export to S3
- **Auth**: AWS Cognito (email/password, Google, Apple)
- **Payments**: Stripe subscriptions
- **Pages**: `/` (landing), `/login`, `/dashboard`, `/chat`, `/docs`, `/tools`
- **Deploy**: `cd website && ./deploy.sh` (builds + syncs to S3 + invalidates CloudFront)

## DeerFlow (Chat UI)

- **URL**: app.minimax.villamarket.ai
- **Source**: `/home/nic/data/deerflow/` (separate repo, Docker containers)
- **Backend**: LangGraph agents calling LiteLLM → vLLM
- **Auth gate**: CloudFront Function redirects unauthenticated users to login
- **Branding**: Customized as villamarket.ai / MiniMax-M2.5

## iOS App

- **Path**: `ios/MiniMaxApp/`
- **Stack**: Swift, SwiftUI, SwiftData
- **API**: SSE streaming via LangGraph endpoints at app.minimax.villamarket.ai
- **Status**: Scaffolded, not yet built

## AWS Infrastructure

| Resource | ID / ARN |
|----------|----------|
| Website CloudFront | E2AFMAXJ9YXUTH |
| Chat CloudFront | E7MNC26N70Y7Z |
| Chat ACM Cert | arn:aws:acm:us-east-1:914499832220:certificate/1efa3355-... |
| Route53 Zone | Z069245539VG1ZOH980UK |
| Cognito Pool | us-east-1 (TBD) |
| S3 Bucket | minimax-villamarket-website |

## Model Info

- **Name**: MiniMax-M2.5
- **Precision**: FP8 (native, ~230 GB)
- **Architecture**: MoE (Mixture of Experts)
- **Context**: 128K tokens
- **Performance**: 80.2% SWE-Bench Verified, 51.3% Multi-SWE-Bench
- **Pricing**: $0.30/M input, $1.20/M output
