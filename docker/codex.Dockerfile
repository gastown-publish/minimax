# Codex CLI — full-featured with all tools pre-installed
FROM node:22-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Codex CLI + Claude Code + Nori + Nori skillsets
RUN npm install -g @openai/codex @anthropic-ai/claude-code nori-ai-cli nori-skillsets

# Playwright MCP plugin (browser testing)
RUN npx -y @anthropic-ai/claude-code mcp add playwright -- npx @anthropic-ai/mcp-server-playwright 2>/dev/null || true

# Install nori senior-swe skillset (17 skills)
RUN nori-skillsets install senior-swe --non-interactive 2>/dev/null || true

# Install mm CLI
RUN pip install --no-cache-dir --break-system-packages minimax-agent || true

# Copy bundled skills into Claude Code's global skills dir
COPY src/minimax_cli/skills/*.md /root/.claude/skills/

# Copy skills + system prompt into mm-claude config
RUN mkdir -p /root/.mm-claude/skills /root/.codex
COPY src/minimax_cli/skills/*.md /root/.mm-claude/skills/
COPY src/minimax_cli/system_prompt.py /tmp/
RUN python3 -c "exec(open('/tmp/system_prompt.py').read()); open('/root/.mm-claude/CLAUDE.md','w').write(CLAUDE_SYSTEM_PROMPT)" \
    && python3 -c "exec(open('/tmp/system_prompt.py').read()); open('/root/.codex/instructions.md','w').write(SYSTEM_PROMPT)" \
    && rm /tmp/system_prompt.py

WORKDIR /app
ENTRYPOINT ["codex"]
