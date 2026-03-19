# OpenCode — full-featured with all tools pre-installed
FROM node:22-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

# OpenCode
RUN curl -fsSL https://opencode.ai/install | bash || true

# Claude Code + Nori + Nori skillsets
RUN npm install -g @anthropic-ai/claude-code nori-ai-cli nori-skillsets

# Playwright MCP plugin (browser testing)
RUN npx -y @anthropic-ai/claude-code mcp add playwright -- npx @anthropic-ai/mcp-server-playwright 2>/dev/null || true

# Install nori senior-swe skillset (17 skills)
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

# Install mm CLI
RUN pip install --no-cache-dir --break-system-packages minimax-agent || true

# Copy bundled skills into Claude Code's global skills dir
COPY src/minimax_cli/skills/*.md /root/.claude/skills/

# Copy skills + system prompt
RUN mkdir -p /root/.mm-claude/skills
COPY src/minimax_cli/skills/*.md /root/.mm-claude/skills/
COPY src/minimax_cli/system_prompt.py /tmp/
RUN python3 -c "exec(open('/tmp/system_prompt.py').read()); open('/root/.mm-claude/CLAUDE.md','w').write(CLAUDE_SYSTEM_PROMPT)" \
    && python3 -c "exec(open('/tmp/system_prompt.py').read()); open('/root/.opencode-instructions.md','w').write(SYSTEM_PROMPT)" \
    && rm /tmp/system_prompt.py

WORKDIR /app
ENTRYPOINT ["opencode"]
