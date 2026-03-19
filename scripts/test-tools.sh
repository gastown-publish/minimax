#!/bin/bash
# Test script for MiniMax Tools + API proxy
# All tests use public URLs only — no localhost required.
#
# Usage:
#   ./scripts/test-tools.sh                  # run all tests (no auth)
#   ./scripts/test-tools.sh sk-your-key      # also run authenticated API tests

set -uo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

PASS=0
FAIL=0
WARN=0

TS="https://api.minimax.villamarket.ai"
SITE="https://minimax.villamarket.ai"
API="https://api.minimax.villamarket.ai"

check() {
  local label="$1" url="$2" expect="$3"
  local code
  code=$(curl -s -L -o /dev/null -w "%{http_code}" --max-time 15 "$url" 2>/dev/null || echo "000")
  if [[ "$code" == "$expect" ]]; then
    echo -e "  ${GREEN}✓${NC} ${label} — HTTP ${code}"
    ((PASS++))
  else
    echo -e "  ${RED}✗${NC} ${label} — HTTP ${code} (expected ${expect})"
    ((FAIL++))
  fi
}

check_contains() {
  local label="$1" url="$2" needle="$3"
  local body
  body=$(curl -s -L --max-time 15 "$url" 2>/dev/null || echo "")
  if echo "$body" | grep -qi "$needle"; then
    echo -e "  ${GREEN}✓${NC} ${label} — contains '${needle}'"
    ((PASS++))
  else
    echo -e "  ${RED}✗${NC} ${label} — missing '${needle}'"
    ((FAIL++))
  fi
}

check_post() {
  local label="$1" url="$2" data="$3" expect="$4"
  shift 4
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 \
    -X POST -H "Content-Type: application/json" "$@" -d "$data" "$url" 2>/dev/null || echo "000")
  if [[ "$code" == "$expect" ]]; then
    echo -e "  ${GREEN}✓${NC} ${label} — HTTP ${code}"
    ((PASS++))
  else
    echo -e "  ${RED}✗${NC} ${label} — HTTP ${code} (expected ${expect})"
    ((FAIL++))
  fi
}

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║        MiniMax Tools & API Test Suite        ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════╝${NC}"
echo ""

# ─── Tools via Public URLs ───
echo -e "${CYAN}[1/5] Tools — Public URLs${NC}"
check "Dify (:8443)"                 "${TS}:8443/"           "200"
check "SearXNG (/minimax-search)"    "${TS}/minimax-search"  "200"
check "DeerFlow (:10000)"           "${TS}:10000/"           "200"
echo ""

# ─── SearXNG full functionality ───
echo -e "${CYAN}[2/5] SearXNG — Assets & Search${NC}"
check      "CSS loads"               "${TS}/static/themes/simple/sxng-ltr.min.css"  "200"
check      "JS loads"                "${TS}/static/themes/simple/sxng-core.min.js"   "200"
check      "Search returns results"  "${TS}/search?q=hello"                          "200"
echo ""

# ─── Dify & DeerFlow content ───
echo -e "${CYAN}[3/5] Dify & DeerFlow — Content Check${NC}"
check_contains "Dify serves Next.js app"  "${TS}:8443/"   "__next"
check_contains "DeerFlow serves Next.js app" "${TS}:10000/" "__next"
echo ""

# ─── MiniMax Website ───
echo -e "${CYAN}[4/5] Website (${SITE})${NC}"
check "Homepage"                      "${SITE}/"       "200"
check "Tools page"                    "${SITE}/tools"  "200"
check "Docs page"                     "${SITE}/docs"   "200"
check "Login page"                    "${SITE}/login"  "200"
check_contains "Tools → Dify card"     "${SITE}/tools" "Dify"
check_contains "Tools → SearXNG card"  "${SITE}/tools" "SearXNG"
check_contains "Tools → DeerFlow card" "${SITE}/tools" "DeerFlow"
check_contains "Tools → open buttons"  "${SITE}/tools" "Open"
echo ""

# ─── API proxy ───
echo -e "${CYAN}[5/5] API Proxy (${API})${NC}"
check "GET  /v1/models (no auth)"          "${API}/v1/models"  "401"
check_post "POST /v1/chat/completions (no auth)" \
  "${API}/v1/chat/completions" \
  '{"model":"MiniMax-M2.5","messages":[{"role":"user","content":"hi"}]}' \
  "401"
check_contains "Returns LiteLLM auth error" "${API}/v1/models" "Authentication Error"

# Authenticated tests if key provided
KEY="${1:-}"
if [[ -n "$KEY" ]]; then
  echo ""
  echo -e "  ${YELLOW}ℹ${NC} Testing with key: ${KEY:0:12}..."

  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 \
    -H "Authorization: Bearer ${KEY}" "${API}/v1/models" 2>/dev/null || echo "000")
  if [[ "$code" == "200" ]]; then
    echo -e "  ${GREEN}✓${NC} GET /v1/models (with key) — HTTP ${code}"
    ((PASS++))
  else
    echo -e "  ${RED}✗${NC} GET /v1/models (with key) — HTTP ${code} (expected 200)"
    ((FAIL++))
  fi

  RESP=$(curl -s --max-time 60 \
    -H "Authorization: Bearer ${KEY}" \
    -H "Content-Type: application/json" \
    -d '{"model":"MiniMax-M2.5","messages":[{"role":"user","content":"Say hello in exactly 5 words."}],"max_tokens":20,"stream":false}' \
    "${API}/v1/chat/completions" 2>/dev/null || echo "")

  if echo "$RESP" | grep -q '"choices"'; then
    CONTENT=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'][:80])" 2>/dev/null || echo "?")
    echo -e "  ${GREEN}✓${NC} POST /v1/chat/completions — response: ${CONTENT}"
    ((PASS++))
  elif echo "$RESP" | grep -q '"error"'; then
    MSG=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['error']['message'][:80])" 2>/dev/null || echo "unknown")
    echo -e "  ${YELLOW}⚠${NC} POST /v1/chat/completions — error: ${MSG}"
    ((WARN++))
  else
    echo -e "  ${RED}✗${NC} POST /v1/chat/completions — no response"
    ((FAIL++))
  fi
else
  echo ""
  echo -e "  ${YELLOW}ℹ${NC} Pass an API key to test authenticated requests:"
  echo -e "  ${YELLOW}ℹ${NC}   ./scripts/test-tools.sh sk-your-key-here"
  ((WARN+=2))
fi

echo ""
echo -e "${BOLD}══════════════════════════════════════════════${NC}"
echo -e "  ${GREEN}✓ Passed: ${PASS}${NC}   ${RED}✗ Failed: ${FAIL}${NC}   ${YELLOW}⚠ Skipped: ${WARN}${NC}"
if [[ $FAIL -eq 0 ]]; then
  echo -e "  ${GREEN}${BOLD}All checks passed!${NC}"
else
  echo -e "  ${RED}${BOLD}Some checks failed — see above${NC}"
fi
echo -e "${BOLD}══════════════════════════════════════════════${NC}"
echo ""

exit $FAIL
