# mm — MiniMax-M2.5 CLI

AI coding agent powered by [MiniMax-M2.5](https://huggingface.co/MiniMaxAI/MiniMax-M2.5) — 456B MoE model on 8x NVIDIA H100 80GB GPUs.

**Website**: [minimax.villamarket.ai](https://minimax.villamarket.ai)
**Chat**: [app.minimax.villamarket.ai](https://app.minimax.villamarket.ai)
**API**: `https://api.minimax.villamarket.ai/v1`

| Benchmark | Score |
|-----------|-------|
| SWE-Bench Verified | **80.2%** |
| Multi-SWE-Bench | **51.3%** |

---

## Install

```bash
curl -fsSL minimax.villamarket.ai/install | sh
```

Or with pip:

```bash
pip install minimax-agent
```

## Quick Start

```bash
# Authenticate
mm auth login

# Chat
mm run

# Launch AI coding tools with MiniMax backend
mm launch claude     # Claude Code
mm launch toad       # Toad TUI (with tools via ACP)
mm launch nori       # Nori TUI
mm launch aider      # Aider
mm launch codex      # Codex CLI
mm launch kimi       # Kimi CLI
mm launch opencode   # OpenCode
mm launch openclaw   # OpenClaw
mm launch gasclaw    # Gasclaw (multi-agent orchestration)

# Iterative development
mm loop "add tests for the auth module"
```

---

## API

**Endpoint**: `https://api.minimax.villamarket.ai/v1`

OpenAI-compatible. All requests require a Bearer token.

```bash
curl https://api.minimax.villamarket.ai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minimax-m2.5",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

| Model ID | Context | Description |
|----------|---------|-------------|
| `minimax-m2.5` | 128K | Recommended |
| `MiniMaxAI/MiniMax-M2.5` | 128K | Full name alias |

### Pricing

| | Price |
|---|---|
| Input | $0.30 / 1M tokens |
| Output | $1.20 / 1M tokens |

---

## Integrations

### Claude Code

```bash
mm launch claude
```

Or manually:

```bash
export ANTHROPIC_BASE_URL="https://api.minimax.villamarket.ai"
export ANTHROPIC_API_KEY="YOUR_API_KEY"
claude --model minimax-m2.5
```

### Codex (OpenAI CLI)

```bash
mm launch codex
```

Or manually:

```bash
export OPENAI_BASE_URL="https://api.minimax.villamarket.ai/v1"
export OPENAI_API_KEY="YOUR_API_KEY"
codex --model minimax-m2.5 "Write a Python function"
```

### Aider

```bash
mm launch aider
```

Or manually:

```bash
aider --openai-api-base https://api.minimax.villamarket.ai/v1 \
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
    "apiBase": "https://api.minimax.villamarket.ai/v1",
    "apiKey": "YOUR_API_KEY"
  }]
}
```

### Cline (VS Code)

1. API Provider: "OpenAI Compatible"
2. Base URL: `https://api.minimax.villamarket.ai/v1`
3. API Key: `YOUR_API_KEY`
4. Model ID: `minimax-m2.5`

### Any OpenAI-compatible client

| Setting | Value |
|---------|-------|
| Base URL | `https://api.minimax.villamarket.ai/v1` |
| API Key | Your API key |
| Model | `minimax-m2.5` |

---

## Code Examples

### Python

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.minimax.villamarket.ai/v1",
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
  baseURL: "https://api.minimax.villamarket.ai/v1",
  apiKey: "YOUR_API_KEY",
});

const response = await client.chat.completions.create({
  model: "minimax-m2.5",
  messages: [{ role: "user", content: "Hello!" }],
});
console.log(response.choices[0].message.content);
```

---

## CLI Commands

```
mm run                    Interactive chat REPL
mm serve                  Start full stack (vLLM + LiteLLM)
mm stop                   Stop all servers
mm ps                     Show running processes, GPU usage
mm logs                   Tail server logs
mm test                   Run inference health checks
mm tui                    Launch admin TUI (key management)
mm auth login             Store API key
mm auth status            Check auth status
mm auth logout            Remove stored key
mm launch <tool>          Launch AI tools with MiniMax backend
mm loop "task"            Ralph Loop — iterative development
mm skills list            List available skills
mm completion install     Install shell autocomplete
mm upgrade                Upgrade to latest version
```

---

## Docker Images

Pre-built Docker images with full AI toolchain on [Docker Hub](https://hub.docker.com/u/thanakijwanavit):

| Image | Primary Tool |
|-------|-------------|
| `thanakijwanavit/mm-claude` | Claude Code |
| `thanakijwanavit/mm-nori` | Nori TUI |
| `thanakijwanavit/mm-toad` | Toad TUI |
| `thanakijwanavit/mm-codex` | Codex CLI |
| `thanakijwanavit/mm-kimi` | Kimi CLI |
| `thanakijwanavit/mm-opencode` | OpenCode |
| `thanakijwanavit/mm-gasclaw` | Gasclaw (multi-agent) |
| `thanakijwanavit/mm` | mm CLI |

Every image includes: Claude Code, Nori, nori-skillsets (senior-swe), Playwright MCP, claude-mem, mm CLI, bundled skills, and system prompts.

```bash
docker run --rm -it -e MINIMAX_API_KEY=sk-xxx thanakijwanavit/mm-claude:latest
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

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for testing rules, key generation, and development workflow.

## Support

Contact: [support@villamarket.ai](mailto:support@villamarket.ai)
