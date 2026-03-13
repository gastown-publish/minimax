# MiniMax-M2.5

Self-hosted [MiniMax-M2.5](https://huggingface.co/MiniMaxAI/MiniMax-M2.5) inference platform running on 8x NVIDIA H100 80GB GPUs.

**Website**: [minimax.villamarket.ai](https://minimax.villamarket.ai)
**Chat**: [app.minimax.villamarket.ai](https://app.minimax.villamarket.ai)

| Component | Description |
|-----------|-------------|
| **vLLM** (port 8080) | Model inference server (TP8 + expert parallel) |
| **LiteLLM** (port 4000) | API proxy with key management and cost tracking |
| **Website** | Landing page, API docs, dashboard, auth (Next.js + S3 + CloudFront) |
| **DeerFlow** | AI agent chat UI at `app.minimax.villamarket.ai` (Next.js + LangGraph) |
| **CLI** | Ollama-style CLI for managing the server |
| **TUI** | Terminal UI for API key management |
| **iOS App** | Native Swift app (in development) |

---

## Project Structure

```
.
├── scripts/                  # Server management scripts
│   ├── start.sh              # Start vLLM server
│   ├── start-all.sh          # Start vLLM + LiteLLM
│   ├── stop.sh               # Stop vLLM
│   ├── stop-all.sh           # Stop everything
│   ├── health.sh             # Health check
│   ├── test.sh               # Inference test
│   ├── test-tools.sh         # Tool calling test
│   └── download-model.sh     # Download model from HuggingFace
├── src/minimax_cli/          # CLI source code
│   ├── main.py               # Entry point
│   ├── api.py                # API client
│   ├── config.py             # Configuration
│   ├── constants.py          # Constants
│   └── commands/             # CLI subcommands
├── tui/                      # Admin TUI (Textual)
│   └── app.py                # Key management interface
├── website/                  # minimax.villamarket.ai
│   ├── src/                  # Next.js source
│   │   ├── app/              # App Router pages
│   │   ├── components/       # React components
│   │   └── lib/              # Utilities + auth
│   ├── lambda/               # AWS Lambda functions
│   │   ├── keys.py           # API key generation
│   │   ├── checkout.py       # Stripe checkout
│   │   ├── stripe_webhook.py # Stripe webhooks
│   │   ├── promo.py          # Promo codes
│   │   └── referral.py       # Referral system
│   ├── cf-function.js        # CloudFront Function
│   └── deploy.sh             # Build + deploy to S3/CloudFront
├── ios/                      # iOS app (Swift)
│   ├── MiniMaxApp/           # App source
│   │   ├── App/              # Entry point + state
│   │   ├── Core/API/         # SSE streaming + LangGraph client
│   │   ├── Core/Models/      # Data models
│   │   └── Features/         # Chat, Threads, Settings views
│   └── Package.swift         # Swift Package manifest
├── litellm-config.example.yaml
├── admin                     # Symlink to TUI launcher
├── pyproject.toml            # Python package config
├── CLAUDE.md                 # AI agent instructions
└── README.md                 # This file
```

---

## CLI

Ollama-style CLI for managing the server and chatting with the model.

### Install

```bash
pip install -e .
```

### Commands

```
minimax run                 Interactive chat REPL with streaming + think blocks
minimax serve               Start full stack (vLLM + LiteLLM)
minimax serve --vllm-only   Start vLLM only
minimax stop                Stop all servers
minimax ps                  Show running processes, GPU usage, uptime
minimax list                List available models
minimax logs                Tail vLLM logs (--litellm for LiteLLM)
minimax test                Run inference health checks
minimax tui                 Launch admin TUI (key management)
minimax auth login          Store API key
minimax auth status         Check auth status
minimax auth logout         Remove stored key
minimax setup claude        Configure Claude Code
minimax setup codex         Configure Codex CLI
minimax setup aider         Configure Aider
minimax setup continue      Configure Continue (VS Code/JetBrains)
minimax setup cline         Print Cline setup instructions
```

### Quick Start

```bash
# Start the server
minimax serve

# Check status
minimax ps

# Start chatting
minimax run

# Configure Claude Code to use this server
minimax auth login
minimax setup claude
```

---

## Benchmarks

| Benchmark | Score |
|-----------|-------|
| SWE-Bench Verified | **80.2%** |
| Multi-SWE-Bench | **51.3%** |

## API Endpoint

```
https://gpu-workspace.taile8dc37.ts.net/minimax/v1
```

All requests require an API key:

```
Authorization: Bearer YOUR_API_KEY
```

## Models

| Model ID | Context | Description |
|----------|---------|-------------|
| `minimax-m2.5` | 128K | Recommended |
| `MiniMaxAI/MiniMax-M2.5` | 128K | Full name alias |

## Pricing

| | Price |
|---|---|
| Input | $0.30 / 1M tokens |
| Output | $1.20 / 1M tokens |

---

## Quick Start

```bash
curl https://gpu-workspace.taile8dc37.ts.net/minimax/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minimax-m2.5",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## Integrations

### Claude Code

```json
{
  "apiProvider": "custom",
  "customApiBaseUrl": "https://gpu-workspace.taile8dc37.ts.net/minimax/v1",
  "customApiKey": "YOUR_API_KEY",
  "customModelId": "minimax-m2.5"
}
```

### Codex (OpenAI CLI)

```bash
export OPENAI_BASE_URL="https://gpu-workspace.taile8dc37.ts.net/minimax/v1"
export OPENAI_API_KEY="YOUR_API_KEY"
codex --model minimax-m2.5 "Write a Python function"
```

### Aider

```bash
aider --openai-api-base https://gpu-workspace.taile8dc37.ts.net/minimax/v1 \
      --openai-api-key YOUR_API_KEY \
      --model openai/minimax-m2.5
```

### Continue (VS Code / JetBrains)

Add to `~/.continue/config.json`:

```json
{
  "models": [{
    "title": "MiniMax-M2.5",
    "provider": "openai",
    "model": "minimax-m2.5",
    "apiBase": "https://gpu-workspace.taile8dc37.ts.net/minimax/v1",
    "apiKey": "YOUR_API_KEY"
  }]
}
```

### Cline (VS Code)

1. API Provider: "OpenAI Compatible"
2. Base URL: `https://gpu-workspace.taile8dc37.ts.net/minimax/v1`
3. API Key: `YOUR_API_KEY`
4. Model ID: `minimax-m2.5`

### Any OpenAI-compatible client

| Setting | Value |
|---------|-------|
| Base URL | `https://gpu-workspace.taile8dc37.ts.net/minimax/v1` |
| API Key | Your API key |
| Model | `minimax-m2.5` |

---

## Code Examples

### Python

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://gpu-workspace.taile8dc37.ts.net/minimax/v1",
    api_key="YOUR_API_KEY",
)

response = client.chat.completions.create(
    model="minimax-m2.5",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

### Python (streaming)

```python
stream = client.chat.completions.create(
    model="minimax-m2.5",
    messages=[{"role": "user", "content": "Write a Redis cache decorator."}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Node.js / TypeScript

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://gpu-workspace.taile8dc37.ts.net/minimax/v1",
  apiKey: "YOUR_API_KEY",
});

const response = await client.chat.completions.create({
  model: "minimax-m2.5",
  messages: [{ role: "user", content: "Hello!" }],
});
console.log(response.choices[0].message.content);
```

---

## API Reference

### POST /v1/chat/completions

Standard OpenAI chat completions endpoint. Supports streaming, function calling, temperature, top_p, max_tokens, stop sequences.

### GET /v1/models

List available models.

### GET /health/liveliness

Health check — returns 200 when ready.

---

## Self-Hosting

### Requirements

- 8x NVIDIA H100 80GB (or equivalent ~640 GB VRAM)
- [vLLM](https://github.com/vllm-project/vllm) v0.15+
- CUDA 12.8+

### Download Model

```bash
pip install huggingface_hub[hf_transfer]
HF_HUB_ENABLE_HF_TRANSFER=1 huggingface-cli download MiniMaxAI/MiniMax-M2.5 \
    --local-dir /path/to/MiniMax-M2.5-HF
```

### Start Server

```bash
vllm serve /path/to/MiniMax-M2.5-HF \
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
    --served-model-name minimax-m2.5 \
    --compilation-config '{"cudagraph_mode": "PIECEWISE"}'
```

### API Key Management

```bash
minimax tui   # or ./admin
```

Keys: `g` generate | `v` view | `e` email key | `b` set budget | `d` delete | `r` refresh | `q` quit

---

## Infrastructure

| Service | URL | Hosting |
|---------|-----|---------|
| Website | minimax.villamarket.ai | S3 + CloudFront |
| Chat UI | app.minimax.villamarket.ai | CloudFront -> Tailscale Funnel -> DeerFlow |
| API | gpu-workspace.taile8dc37.ts.net/minimax/v1 | Tailscale Funnel -> LiteLLM |

## Rate Limits

- Max concurrent requests: 16
- Max context length: 131,072 tokens (128K)
- Request timeout: 600 seconds

## Support

Contact: [support@villamarket.ai](mailto:support@villamarket.ai)
