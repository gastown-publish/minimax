#!/bin/bash

# Health check for vLLM and LiteLLM backends
# Returns 0 if both healthy, 1 if either is down

set -e

echo "=== Health Check ==="

# Check vLLM on port 8080
echo -n "vLLM (port 8080): "
if curl -sf http://localhost:8080/health >/dev/null 2>&1; then
    echo "HEALTHY"
    VLLM_STATUS=0
else
    echo "DOWN"
    VLLM_STATUS=1
fi

# Check LiteLLM on port 4000
echo -n "LiteLLM (port 4000): "
if curl -sf http://localhost:4000/health >/dev/null 2>&1; then
    echo "HEALTHY"
    LITELLM_STATUS=0
else
    echo "DOWN"
    LITELLM_STATUS=1
fi

# Return exit code based on both services
if [ "$VLLM_STATUS" -eq 0 ] && [ "$LITELLM_STATUS" -eq 0 ]; then
    echo ""
    echo "All services healthy"
    exit 0
else
    echo ""
    echo "One or more services down"
    exit 1
fi