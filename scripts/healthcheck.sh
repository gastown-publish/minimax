#!/bin/bash
# healthcheck.sh — Verify vLLM and LiteLLM backend connectivity
# Exit code 0 = healthy, 1 = unhealthy

set -e

VLLM_PORT=8080
LITELLM_PORT=4000

# Check vLLM
echo "Checking vLLM on port $VLLM_PORT..."
VLLM_CODE=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:${VLLM_PORT}/health" 2>/dev/null || echo "000")
if [ "$VLLM_CODE" != "200" ]; then
    echo "❌ vLLM unhealthy (HTTP $VLLM_CODE)"
    exit 1
fi
echo "✅ vLLM healthy"

# Check LiteLLM
echo "Checking LiteLLM on port $LITELLM_PORT..."
LITELLM_CODE=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:${LITELLM_PORT}/health" 2>/dev/null || echo "000")
if [ "$LITELLM_CODE" != "200" ]; then
    echo "❌ LiteLLM unhealthy (HTTP $LITELLM_CODE)"
    exit 1
fi
echo "✅ LiteLLM healthy"

echo ""
echo "=== All backends healthy ==="
exit 0