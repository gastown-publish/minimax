#!/bin/bash

PORT=8080
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:${PORT}/health 2>/dev/null)

if [ "$HTTP_CODE" != "200" ]; then
    echo "OFFLINE — Server is not responding on port $PORT (HTTP $HTTP_CODE)"
    exit 1
fi

echo "HEALTHY — vLLM server is ready"

# Show models
echo ""
echo "Models:"
curl -s http://localhost:${PORT}/v1/models 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
for m in d.get('data',[]):
    print(f'  {m[\"id\"]}')
" 2>/dev/null

# Show GPU usage
echo ""
echo "GPU Memory:"
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader

# Show process info
PID=$(pgrep -f "vllm.entrypoints" 2>/dev/null | head -1 || true)
if [ -n "$PID" ]; then
    RSS=$(ps -p "$PID" -o rss --no-headers 2>/dev/null | awk '{printf "%.1f", $1/1024/1024}')
    UPTIME=$(ps -p "$PID" -o etime --no-headers 2>/dev/null | xargs)
    echo ""
    echo "Process: PID $PID, RSS ${RSS} GB, Uptime: $UPTIME"
fi

# Check LiteLLM
echo ""
LITELLM_HEALTH=$(curl -s http://localhost:4000/health 2>/dev/null)
if [ -n "$LITELLM_HEALTH" ]; then
    echo "LiteLLM: HEALTHY (port 4000)"
else
    echo "LiteLLM: OFFLINE (port 4000)"
fi
