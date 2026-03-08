# MiniMax-M2.5

Self-hosted [MiniMax-M2.5](https://huggingface.co/MiniMaxAI/MiniMax-M2.5) inference server — 128K context, function calling, reasoning, optimized for coding.

Running on 8x NVIDIA H100 80GB with vLLM (tensor parallel + expert parallel), exposed as an **OpenAI-compatible API**.

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
minimax setup openclaw      Configure OpenClaw
minimax setup opencode      Configure OpenCode
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

## Integrations

### Claude Code

Add as a custom API provider in your Claude Code settings:

```bash
# In your project's .claude/settings.json or ~/.claude/settings.json
```

```json
{
  "apiProvider": "custom",
  "customApiBaseUrl": "https://gpu-workspace.taile8dc37.ts.net/minimax/v1",
  "customApiKey": "YOUR_API_KEY",
  "customModelId": "minimax-m2.5"
}
```

Or set via environment variables:

```bash
export ANTHROPIC_BASE_URL="https://gpu-workspace.taile8dc37.ts.net/minimax/v1"
export ANTHROPIC_API_KEY="YOUR_API_KEY"
claude --model minimax-m2.5
```

### OpenClaw

Add to your `openclaw.json` in `models.providers`:

```json
{
  "id": "minimax",
  "name": "MiniMax-M2.5",
  "api": "openai-completions",
  "baseUrl": "https://gpu-workspace.taile8dc37.ts.net/minimax/v1",
  "apiKey": "YOUR_API_KEY",
  "timeout": 600000,
  "models": [
    {
      "id": "minimax-m2.5",
      "name": "MiniMax-M2.5 (128K)",
      "contextWindow": 131072,
      "maxTokens": 131072
    }
  ]
}
```

Then set as default:

```bash
openclaw config set model "minimax/minimax-m2.5"
```

### Codex (OpenAI CLI)

Codex supports any OpenAI-compatible endpoint:

```bash
export OPENAI_BASE_URL="https://gpu-workspace.taile8dc37.ts.net/minimax/v1"
export OPENAI_API_KEY="YOUR_API_KEY"

codex --model minimax-m2.5 "Write a Python function to merge two sorted lists"
```

Or configure in `~/.codex/config.yaml`:

```yaml
provider: openai
model: minimax-m2.5
base_url: https://gpu-workspace.taile8dc37.ts.net/minimax/v1
api_key: YOUR_API_KEY
```

### OpenCode

Configure in `~/.opencode/config.json`:

```json
{
  "provider": {
    "name": "openai-compatible",
    "apiBase": "https://gpu-workspace.taile8dc37.ts.net/minimax/v1",
    "apiKey": "YOUR_API_KEY",
    "model": "minimax-m2.5"
  }
}
```

Or use environment variables:

```bash
export OPENAI_API_BASE="https://gpu-workspace.taile8dc37.ts.net/minimax/v1"
export OPENAI_API_KEY="YOUR_API_KEY"

opencode --model minimax-m2.5
```

### Aider

```bash
aider --openai-api-base https://gpu-workspace.taile8dc37.ts.net/minimax/v1 \
      --openai-api-key YOUR_API_KEY \
      --model openai/minimax-m2.5
```

Or set in `~/.aider.conf.yml`:

```yaml
openai-api-base: https://gpu-workspace.taile8dc37.ts.net/minimax/v1
openai-api-key: YOUR_API_KEY
model: openai/minimax-m2.5
```

### Continue (VS Code / JetBrains)

Add to `~/.continue/config.json`:

```json
{
  "models": [
    {
      "title": "MiniMax-M2.5",
      "provider": "openai",
      "model": "minimax-m2.5",
      "apiBase": "https://gpu-workspace.taile8dc37.ts.net/minimax/v1",
      "apiKey": "YOUR_API_KEY"
    }
  ]
}
```

### Cline (VS Code)

In Cline settings:
1. Set **API Provider** to "OpenAI Compatible"
2. **Base URL**: `https://gpu-workspace.taile8dc37.ts.net/minimax/v1`
3. **API Key**: `YOUR_API_KEY`
4. **Model ID**: `minimax-m2.5`

### Open WebUI

In Settings → Connections → OpenAI:
- **URL**: `https://gpu-workspace.taile8dc37.ts.net/minimax/v1`
- **API Key**: `YOUR_API_KEY`

### LibreChat

Add to `librechat.yaml`:

```yaml
endpoints:
  custom:
    - name: "MiniMax-M2.5"
      apiKey: "YOUR_API_KEY"
      baseURL: "https://gpu-workspace.taile8dc37.ts.net/minimax/v1"
      models:
        default: ["minimax-m2.5"]
```

### Any OpenAI-compatible client

This API is fully OpenAI-compatible. Use these settings in any client:

| Setting | Value |
|---------|-------|
| Base URL | `https://gpu-workspace.taile8dc37.ts.net/minimax/v1` |
| API Key | Your API key |
| Model | `minimax-m2.5` |

---

## Code Examples

### Python (openai SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://gpu-workspace.taile8dc37.ts.net/minimax/v1",
    api_key="YOUR_API_KEY",
)

response = client.chat.completions.create(
    model="minimax-m2.5",
    messages=[
        {"role": "system", "content": "You are a senior software engineer."},
        {"role": "user", "content": "Write a Python function to merge two sorted lists."},
    ],
    max_tokens=1024,
    temperature=0.6,
)

print(response.choices[0].message.content)
```

### Python (streaming)

```python
stream = client.chat.completions.create(
    model="minimax-m2.5",
    messages=[{"role": "user", "content": "Write a Redis cache decorator in Python."}],
    max_tokens=2048,
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Python (function calling)

```python
import json

tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_sql",
            "description": "Execute a SQL query against the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The SQL query"},
                    "database": {"type": "string", "description": "Database name"},
                },
                "required": ["query"],
            },
        },
    }
]

response = client.chat.completions.create(
    model="minimax-m2.5",
    messages=[{"role": "user", "content": "Find all users who signed up in the last 7 days"}],
    tools=tools,
    tool_choice="auto",
)

message = response.choices[0].message
if message.tool_calls:
    for call in message.tool_calls:
        print(f"Function: {call.function.name}")
        print(f"Arguments: {call.function.arguments}")
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
  messages: [
    { role: "system", content: "You are a helpful coding assistant." },
    { role: "user", content: "Write a TypeScript function to debounce async functions." },
  ],
  max_tokens: 1024,
});

console.log(response.choices[0].message.content);
```

### cURL

```bash
curl https://gpu-workspace.taile8dc37.ts.net/minimax/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minimax-m2.5",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 1024,
    "stream": true
  }'
```

---

## API Reference

### POST /v1/chat/completions

Standard OpenAI chat completions endpoint. Supports:
- System, user, assistant, and tool messages
- Streaming (`"stream": true`)
- Function calling / tool use
- Temperature, top_p, max_tokens, stop sequences

### GET /v1/models

List available models.

### GET /health/liveliness

Health check — returns 200 when the server is ready.

---

## Reasoning

MiniMax-M2.5 includes chain-of-thought reasoning in `<think>` blocks:

```
<think>
The user wants a binary search implementation...
Let me consider edge cases...
</think>

Here's the implementation:
...
```

The API separates reasoning into the `reasoning_content` field when available. You can also strip `<think>...</think>` blocks from the `content` field.

---

## Rate Limits

- Max concurrent requests: 16
- Max context length: 131,072 tokens (128K)
- Request timeout: 600 seconds

## Capabilities

- **Code generation**: Python, TypeScript, Rust, Go, Java, C++, etc.
- **Code review**: Bug detection, security analysis, refactoring suggestions
- **Function calling**: Native tool use with structured JSON arguments
- **Reasoning**: Step-by-step problem solving with visible thought process
- **Long context**: Process entire codebases, long documents, multi-file diffs
- **Multi-file editing**: 51.3% on Multi-SWE-Bench

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

The admin TUI manages API keys via [LiteLLM](https://github.com/BerriAI/litellm):

```bash
minimax tui
```

Keys: `g` generate | `v` view | `e` email key | `b` set budget | `d` delete | `r` refresh | `q` quit

Generated keys are persisted locally in `~/.config/minimax/keys.json` so they can be viewed anytime (not just at creation). When generating a key, you can provide an email to automatically send the key to the user via SES.

---

## Support

For API key requests or issues, contact the server admin.
