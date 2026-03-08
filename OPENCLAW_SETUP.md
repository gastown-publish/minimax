# MiniMax-M2.5 with OpenClaw Setup Guide

This guide explains how to configure OpenClaw to use your local MiniMax-M2.5 deployment as an AI provider.

## What is OpenClaw?

[OpenClaw](https://openclaw.ai/) is a free and open-source autonomous AI agent developed by Peter Steinberger that integrates AI models with messaging platforms like Signal, Telegram, Discord, WhatsApp, Slack, and many others. It allows you to interact with AI models through the chat apps you already use, with support for browsing the web, running shell commands, managing files, and integrating with 50+ third-party services.

OpenClaw supports multiple AI providers including Anthropic, OpenAI, and custom OpenAI-compatible endpoints (like your local MiniMax-M2.5 deployment).

## Prerequisites

1. **MiniMax-M2.5 server running**: Ensure your MiniMax-M2.5 server is running on port 8080 (vLLM) or port 4000 (LiteLLM proxy)
2. **OpenClaw installed**: Install OpenClaw from [https://github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)

### Verify MiniMax-M2.5 is Running

```bash
cd /home/nic/data/models/MiniMax-M2.5
./scripts/health.sh
```

If not running, start the server:

```bash
# Start full stack (vLLM + LiteLLM with API key auth)
./scripts/start-all.sh

# OR start vLLM only (no API key auth)
./scripts/start.sh
```

## Available Endpoints

Your MiniMax-M2.5 deployment exposes multiple endpoints:

| Endpoint | Authentication | Use Case |
|----------|----------------|----------|
| `http://localhost:8080/v1` | None | Direct vLLM access (local only) |
| `http://localhost:4000/v1` | API Key required | LiteLLM proxy with cost tracking |
| `https://gpu-workspace.taile8dc37.ts.net/minimax/v1` | API Key required | Public Tailscale endpoint |

**Recommendation**: Use `http://localhost:8080/v1` for local OpenClaw setup (fastest, no auth overhead).

## Configuration Methods

OpenClaw provides two ways to configure custom providers:

### Method 1: Interactive Wizard (Recommended)

Run the onboarding wizard:

```bash
openclaw onboard
```

Or use the configuration wizard:

```bash
openclaw config wizard
```

Follow the prompts to add a custom OpenAI-compatible provider.

### Method 2: Manual Configuration

Edit your OpenClaw configuration file:

```bash
openclaw config edit
```

Or manually edit the file shown by:

```bash
openclaw doctor
```

## OpenClaw Configuration

Add the following configuration to your `openclaw.json` file in the `models.providers` section:

### Option A: Direct vLLM (No Authentication)

```json
{
  "models": {
    "mode": "merge",
    "providers": [
      {
        "id": "minimax-local",
        "name": "MiniMax-M2.5 (Local)",
        "api": "openai-completions",
        "baseUrl": "http://localhost:8080/v1",
        "apiKey": "none",
        "models": [
          {
            "id": "MiniMaxAI/MiniMax-M2.5",
            "name": "MiniMax-M2.5 (128K context)",
            "contextWindow": 131072,
            "maxTokens": 131072,
            "description": "MiniMax-M2.5 with 128K context window, FP8 precision, expert parallel across 8x H100"
          }
        ]
      }
    ]
  }
}
```

### Option B: LiteLLM Proxy (With API Key)

```json
{
  "models": {
    "mode": "merge",
    "providers": [
      {
        "id": "minimax-litellm",
        "name": "MiniMax-M2.5 (LiteLLM)",
        "api": "openai-completions",
        "baseUrl": "http://localhost:4000/v1",
        "apiKey": "sk-1564f41cd82a7303e6e3eb15cedc15eb76d1a3f556d8b890",
        "models": [
          {
            "id": "minimax-m2.5",
            "name": "MiniMax-M2.5 via LiteLLM",
            "contextWindow": 131072,
            "maxTokens": 131072,
            "description": "MiniMax-M2.5 with cost tracking and API key auth"
          }
        ]
      }
    ]
  }
}
```

### Configuration Notes

- **`models.mode: "merge"`**: Keeps hosted models (like OpenAI, Anthropic) available as fallbacks
- **`api: "openai-completions"`**: Tells OpenClaw this is an OpenAI-compatible endpoint
- **`baseUrl`**: Must end with `/v1` for OpenAI compatibility
- **`apiKey`**: Set to `"none"` for direct vLLM, or use the master key from `litellm-config.yaml` for LiteLLM
- **`contextWindow`**: MiniMax-M2.5 supports 128K tokens (131072)
- **`maxTokens`**: Maximum output tokens

## Verify Configuration

After adding the configuration, verify OpenClaw can see your model:

```bash
openclaw models list
```

You should see `minimax-local/MiniMaxAI/MiniMax-M2.5` (or your configured provider/model ID) in the list.

## Using MiniMax-M2.5 in OpenClaw

### Set as Default Model

```bash
openclaw config set model "minimax-local/MiniMaxAI/MiniMax-M2.5"
```

### Use in Chat

In any OpenClaw-connected messaging platform, you can:

```
@openclaw use minimax-local/MiniMaxAI/MiniMax-M2.5
```

Or reference it in your chat:

```
/model minimax-local/MiniMaxAI/MiniMax-M2.5
```

## Model Capabilities

MiniMax-M2.5 supports:

- **128K Context Window**: Handle extremely long conversations and documents
- **Function Calling**: Native tool use support (via `--tool-call-parser minimax_m2`)
- **Reasoning**: Separates `<think>` blocks (via `--reasoning-parser minimax_m2_append_think`)
- **Streaming**: Real-time response streaming
- **SWE-Bench**: 80.2% on SWE-Bench Verified, 51.3% on Multi-SWE-Bench

## Advanced Configuration

### Using Environment Variables for API Keys

For better security, store the API key in an environment variable:

1. Add to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
export MINIMAX_API_KEY="sk-1564f41cd82a7303e6e3eb15cedc15eb76d1a3f556d8b890"
```

2. In OpenClaw config, reference the environment variable:

```json
{
  "apiKey": "${MINIMAX_API_KEY}"
}
```

### Multiple Model Variants

You can configure both model names exposed by LiteLLM:

```json
{
  "models": [
    {
      "id": "minimax-m2.5",
      "name": "MiniMax-M2.5 (short name)",
      "contextWindow": 131072,
      "maxTokens": 131072
    },
    {
      "id": "MiniMaxAI/MiniMax-M2.5",
      "name": "MiniMax-M2.5 (full name)",
      "contextWindow": 131072,
      "maxTokens": 131072
    }
  ]
}
```

### Request Timeouts

For long-running tasks, adjust the timeout:

```json
{
  "api": "openai-completions",
  "baseUrl": "http://localhost:8080/v1",
  "apiKey": "none",
  "timeout": 600000
}
```

## Troubleshooting

### OpenClaw Can't Connect

1. **Check server is running**:
   ```bash
   cd /home/nic/data/models/MiniMax-M2.5
   ./scripts/health.sh
   ```

2. **Test endpoint directly**:
   ```bash
   curl http://localhost:8080/v1/models
   ```

3. **Check logs**:
   ```bash
   tail -f /tmp/vllm-minimax.log
   tail -f /tmp/litellm-minimax.log
   ```

### Model Not Listed

Run diagnostics:

```bash
openclaw doctor
openclaw models list
```

Ensure your configuration file is valid JSON and the `baseUrl` ends with `/v1`.

### Slow Responses

- MiniMax-M2.5 uses ~230 GB VRAM and loads in 10-20 minutes on first start
- Initial requests may be slower due to CUDA graph compilation
- Prefix caching speeds up repeated system prompts

### Authentication Errors

If using LiteLLM (port 4000):

1. Verify API key matches `litellm-config.yaml`:
   ```bash
   cat /home/nic/data/models/MiniMax-M2.5/litellm-config.yaml | grep master_key
   ```

2. Use the correct key in OpenClaw config

If using direct vLLM (port 8080):

1. Set `apiKey: "none"` in OpenClaw config
2. No authentication is required

## Cost Tracking (LiteLLM Only)

When using the LiteLLM endpoint (port 4000), costs are tracked in PostgreSQL:

- **Input**: $0.30 / 1M tokens
- **Output**: $1.20 / 1M tokens

View usage via the admin TUI:

```bash
cd /home/nic/data/models/MiniMax-M2.5
./admin
```

## Performance Notes

- **FP8 Precision**: Faster loading and inference than INT4 models
- **Expert Parallel**: Required for MoE routing across 8 GPUs (`--enable-expert-parallel`)
- **Prefix Caching**: Reuses system prompt KV cache for faster follow-up requests
- **Chunked Prefill**: Enables better batching for long context requests

## Comparison: OpenClaw vs. Ollama

| Feature | OpenClaw | Ollama |
|---------|----------|--------|
| Purpose | AI agent with messaging app integration | Local model runner with simple API |
| Integrations | 50+ services, messaging platforms | Basic OpenAI-compatible API |
| Model Support | Multiple providers (OpenAI, Anthropic, custom) | Local models only (GGUF format) |
| Tool Use | Native support with web browsing, file ops | Limited (requires specific formats) |
| Setup Complexity | More complex (requires configuration) | Simple (pull and run) |

**Use OpenClaw if you want**: An AI assistant integrated into your existing workflows and messaging apps with advanced capabilities.

**Use Ollama if you want**: Simple local model hosting with minimal configuration.

## References

### OpenClaw Documentation
- [OpenClaw Official Site](https://openclaw.ai/)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [Model Providers Documentation](https://docs.openclaw.ai/concepts/model-providers)
- [OpenAI Provider Configuration](https://docs.openclaw.ai/providers/openai)
- [Custom Model Configuration Guide](https://blog.laozhang.ai/en/posts/openclaw-custom-model)

### MiniMax-M2.5 Resources
- [Hugging Face Model Card](https://huggingface.co/MiniMaxAI/MiniMax-M2.5)
- [vLLM Documentation](https://docs.vllm.ai/)
- [LiteLLM Documentation](https://docs.litellm.ai/)

### Related Guides
- [OpenClaw with vLLM on AMD](https://www.amd.com/en/developer/resources/technical-articles/2026/openclaw-with-vllm-running-for-free-on-amd-developer-cloud-.html)
- [Free AI Models for OpenClaw](https://lumadock.com/tutorials/free-ai-models-openclaw)
- [Ollama Integration with OpenClaw](https://medium.com/@jacklandrin/clawdbot-moltbot-ollama-as-your-personal-assistant-32f2bdb4a6bc)

## Additional Frontends

Besides OpenClaw, you can integrate MiniMax-M2.5 with other OpenAI-compatible frontends:

### Open WebUI

[Open WebUI](https://github.com/open-webui/open-webui) is a user-friendly web interface for LLMs (similar to ChatGPT's interface).

**Setup**:

1. Install Open WebUI:
   ```bash
   docker run -d -p 3000:8080 -e OPENAI_API_BASE_URL=http://localhost:8080/v1 -e OPENAI_API_KEY=none ghcr.io/open-webui/open-webui:main
   ```

2. Access at `http://localhost:3000`

3. In Settings > Connections, add:
   - **URL**: `http://localhost:8080/v1`
   - **API Key**: `none` (or use LiteLLM endpoint with key)
   - **Model IDs**: `MiniMaxAI/MiniMax-M2.5`

### SillyTavern

[SillyTavern](https://github.com/SillyTavern/SillyTavern) is a frontend for conversational AI with character support.

**Setup**:

1. In API Settings, select "Chat Completion (OpenAI Compatible)"
2. Set **API URL**: `http://localhost:8080/v1`
3. Set **Model**: `MiniMaxAI/MiniMax-M2.5`
4. Leave API Key empty (or use LiteLLM key)

### LibreChat

[LibreChat](https://github.com/danny-avila/LibreChat) is an enhanced ChatGPT clone.

**Setup**:

Add to `librechat.yaml`:

```yaml
endpoints:
  custom:
    - name: "MiniMax-M2.5"
      apiKey: "none"
      baseURL: "http://localhost:8080/v1"
      models:
        default: ["MiniMaxAI/MiniMax-M2.5"]
      titleConvo: true
      titleModel: "MiniMaxAI/MiniMax-M2.5"
```

## Next Steps

1. **Test basic chat**: Start a conversation through OpenClaw in your preferred messaging app
2. **Try tool use**: Ask OpenClaw to browse a website or run a shell command
3. **Experiment with long context**: Feed it a large codebase or long document
4. **Monitor performance**: Use the admin TUI to track usage and costs

For issues or questions, refer to:
- MiniMax-M2.5 deployment: See `/home/nic/data/models/MiniMax-M2.5/CLAUDE.md`
- OpenClaw support: [GitHub Discussions](https://github.com/openclaw/openclaw/discussions)
