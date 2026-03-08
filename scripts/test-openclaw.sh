#!/bin/bash
# Test OpenClaw integration with MiniMax-M2.5

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "OpenClaw Integration Test"
echo "========================================"
echo

# Test 1: Check if vLLM is running
echo "[1/5] Checking if MiniMax-M2.5 vLLM server is running..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✓ vLLM server is running on port 8080"
else
    echo "✗ vLLM server is NOT running on port 8080"
    echo "  Run: cd $REPO_DIR && ./scripts/start.sh"
    exit 1
fi
echo

# Test 2: Check if models endpoint works
echo "[2/5] Testing /v1/models endpoint..."
MODELS_RESPONSE=$(curl -s http://localhost:8080/v1/models)
if echo "$MODELS_RESPONSE" | grep -q "MiniMax"; then
    echo "✓ Models endpoint is working"
    echo "  Available models:"
    echo "$MODELS_RESPONSE" | grep -o '"id":"[^"]*"' | sed 's/"id":"/  - /' | sed 's/"//'
else
    echo "✗ Models endpoint is not returning expected data"
    echo "  Response: $MODELS_RESPONSE"
    exit 1
fi
echo

# Test 3: Test chat completions endpoint
echo "[3/5] Testing /v1/chat/completions endpoint..."
CHAT_RESPONSE=$(curl -s http://localhost:8080/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "MiniMaxAI/MiniMax-M2.5",
        "messages": [{"role": "user", "content": "Say hello in exactly 3 words"}],
        "max_tokens": 10,
        "temperature": 0
    }')

if echo "$CHAT_RESPONSE" | grep -q "content"; then
    echo "✓ Chat completions endpoint is working"
    CONTENT=$(echo "$CHAT_RESPONSE" | grep -o '"content":"[^"]*"' | head -1 | sed 's/"content":"//' | sed 's/"//')
    echo "  Response: $CONTENT"
else
    echo "✗ Chat completions endpoint failed"
    echo "  Response: $CHAT_RESPONSE"
    exit 1
fi
echo

# Test 4: Check if LiteLLM is running (optional)
echo "[4/5] Checking if LiteLLM proxy is running (optional)..."
if curl -s http://localhost:4000/health > /dev/null 2>&1; then
    echo "✓ LiteLLM proxy is running on port 4000"
    echo "  This enables API key authentication and cost tracking"
else
    echo "⚠ LiteLLM proxy is NOT running on port 4000"
    echo "  This is optional. To enable: cd $REPO_DIR && ./scripts/start-all.sh"
fi
echo

# Test 5: Show OpenClaw configuration example
echo "[5/5] OpenClaw configuration example:"
echo
echo "Add this to your openclaw.json file (models.providers section):"
echo
cat << 'EOF'
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
      "maxTokens": 131072
    }
  ]
}
EOF
echo
echo "Or copy the full example:"
echo "  $REPO_DIR/openclaw-config-example.json"
echo

echo "========================================"
echo "✓ All tests passed!"
echo "========================================"
echo
echo "Next steps:"
echo "  1. Install OpenClaw: https://github.com/openclaw/openclaw"
echo "  2. Configure OpenClaw with the example above"
echo "  3. Run: openclaw models list"
echo "  4. Set as default: openclaw config set model 'minimax-local/MiniMaxAI/MiniMax-M2.5'"
echo
echo "For full documentation, see:"
echo "  $REPO_DIR/OPENCLAW_SETUP.md"
