FROM node:22-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git python3 python3-pip python3-venv curl \
    && rm -rf /var/lib/apt/lists/*

# Claude Code + Nori + Nori skillsets
RUN npm install -g @anthropic-ai/claude-code nori-ai-cli nori-skillsets

# Playwright MCP plugin (for browser testing)
RUN npx -y @anthropic-ai/claude-code mcp add playwright -- npx @anthropic-ai/mcp-server-playwright 2>/dev/null || true

# Install nori senior-swe skillset (skills for Claude Code)
RUN nori-skillsets install senior-swe --non-interactive 2>/dev/null || true

# claude-mem — persistent memory across sessions
RUN git clone --depth 1 https://github.com/thedotmack/claude-mem.git \
        /root/.claude/plugins/marketplaces/thedotmack \
    && cd /root/.claude/plugins/marketplaces/thedotmack/plugin \
    && npm install --production 2>/dev/null || true \
    && mkdir -p /root/.claude/plugins/cache/thedotmack/claude-mem/latest \
    && cp -r /root/.claude/plugins/marketplaces/thedotmack/plugin/* \
             /root/.claude/plugins/cache/thedotmack/claude-mem/latest/ \
    && printf '{"version":2,"plugins":{"claude-mem@thedotmack":[{"scope":"user","installPath":"/root/.claude/plugins/cache/thedotmack/claude-mem/latest","version":"latest","installedAt":"2026-01-01T00:00:00.000Z","lastUpdated":"2026-01-01T00:00:00.000Z"}]}}\n' \
        > /root/.claude/plugins/installed_plugins.json \
    && printf '{"thedotmack":{"source":{"source":"github","repo":"thedotmack/claude-mem"},"installLocation":"/root/.claude/plugins/marketplaces/thedotmack","lastUpdated":"2026-01-01T00:00:00.000Z"}}\n' \
        > /root/.claude/plugins/known_marketplaces.json

# Install mm CLI (for mm loop, mm acp, etc.)
RUN pip install --no-cache-dir --break-system-packages minimax-agent || true

# Copy bundled skills into Claude Code's global skills dir
COPY src/minimax_cli/skills/*.md /root/.claude/skills/

# Copy CLAUDE.md system prompt into mm-claude config
RUN mkdir -p /root/.mm-claude
COPY src/minimax_cli/system_prompt.py /tmp/
RUN python3 -c "exec(open('/tmp/system_prompt.py').read()); open('/root/.mm-claude/CLAUDE.md','w').write(CLAUDE_SYSTEM_PROMPT)" \
    && rm /tmp/system_prompt.py

WORKDIR /app
ENTRYPOINT ["claude"]
