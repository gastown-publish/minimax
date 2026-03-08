#!/bin/bash

PORT=8080
MODEL="MiniMaxAI/MiniMax-M2.5"

run_test() {
    local name="$1"
    local payload="$2"
    local check="$3"

    echo "=== Test: $name ==="
    RESPONSE=$(curl -s http://localhost:${PORT}/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d "$payload" 2>&1)

    if ! echo "$RESPONSE" | grep -q '"choices"'; then
        echo "FAIL — No choices in response:"
        echo "$RESPONSE" | head -5
        echo ""
        return 1
    fi

    CONTENT=$(echo "$RESPONSE" | python3 -c "
import sys,json
m=json.load(sys.stdin)['choices'][0]['message']
print(m.get('content') or '(no content)')
" 2>/dev/null)

    REASONING=$(echo "$RESPONSE" | python3 -c "
import sys,json
m=json.load(sys.stdin)['choices'][0]['message']
r=m.get('reasoning_content','')
print(r[:200] + '...' if len(r) > 200 else r)
" 2>/dev/null)

    PROMPT_N=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['usage']['prompt_tokens'])" 2>/dev/null)
    GEN_N=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['usage']['completion_tokens'])" 2>/dev/null)

    echo "Response: $CONTENT"
    if [ -n "$REASONING" ]; then
        echo "Reasoning: $REASONING"
    fi
    echo "Tokens: prompt=$PROMPT_N, completion=$GEN_N"

    if [ -n "$check" ]; then
        if echo "$RESPONSE" | grep -q "$check"; then
            echo "PASS"
        else
            echo "WARN — Expected pattern '$check' not found"
        fi
    else
        echo "PASS"
    fi
    echo ""
}

echo "Testing MiniMax-M2.5 inference..."
echo ""

# Test 1: Basic inference
run_test "Basic inference" '{
    "model": "'"$MODEL"'",
    "messages": [{"role": "user", "content": "What is 2+2? Answer with just the number."}],
    "max_tokens": 50,
    "temperature": 0
}'

# Test 2: Code generation
run_test "Code generation" '{
    "model": "'"$MODEL"'",
    "messages": [{"role": "user", "content": "Write a Python function that checks if a number is prime. Just the function, no explanation."}],
    "max_tokens": 200,
    "temperature": 0
}' "def"

# Test 3: Tool calling
run_test "Tool calling" '{
    "model": "'"$MODEL"'",
    "messages": [{"role": "user", "content": "What is the weather in San Francisco?"}],
    "tools": [{"type": "function", "function": {"name": "get_weather", "description": "Get the weather for a location", "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}}],
    "max_tokens": 200,
    "temperature": 0
}' "tool_calls"

# Test 4: Reasoning
run_test "Reasoning" '{
    "model": "'"$MODEL"'",
    "messages": [{"role": "user", "content": "Solve step by step: If a train travels 120 km in 2 hours, what is its average speed?"}],
    "max_tokens": 300,
    "temperature": 0
}' "60"

echo "=== All tests complete ==="
