# Gasclaw Docker image — multi-agent orchestration with full toolchain
FROM python:3.13-slim-bookworm

ARG TARGETPLATFORM
ARG TARGETARCH=amd64

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git tmux ca-certificates gnupg \
    && rm -rf /var/lib/apt/lists/*

# Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Go 1.25
RUN curl -fsSL https://go.dev/dl/go1.25.7.linux-${TARGETARCH}.tar.gz | tar -C /usr/local -xzf - || true
ENV PATH="/usr/local/go/bin:/root/go/bin:${PATH}"

# Dolt
RUN curl -fsSL https://github.com/dolthub/dolt/releases/latest/download/dolt-linux-${TARGETARCH}.tar.gz | \
    tar -C /usr/local/bin -xzf - --strip-components=1 dolt-linux-${TARGETARCH}/bin/dolt || true

# Claude Code + Nori + Nori skillsets + OpenClaw
RUN npm install -g @anthropic-ai/claude-code nori-ai-cli nori-skillsets openclaw

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

# Kimi CLI + mm CLI
RUN pip install --no-cache-dir kimi-cli minimax-agent

# Gastown + Beads
RUN go install github.com/steveyegge/gastown/cmd/gt@v0.10.0 || true
RUN go install github.com/steveyegge/beads/cmd/bd@latest || true

# AIS session manager
RUN curl -sL https://raw.githubusercontent.com/gastown-publish/ais/main/bin/ais \
    -o /usr/local/bin/ais && chmod +x /usr/local/bin/ais || true

# Install gasclaw from GitHub
RUN pip install --no-cache-dir git+https://github.com/gastown-publish/gasclaw.git || true

# Copy bundled skills into Claude Code's global skills dir
COPY src/minimax_cli/skills/*.md /root/.claude/skills/

# Copy skills + system prompt
RUN mkdir -p /root/.mm-claude/skills
COPY src/minimax_cli/skills/*.md /root/.mm-claude/skills/
COPY src/minimax_cli/system_prompt.py /tmp/
RUN python3 -c "exec(open('/tmp/system_prompt.py').read()); open('/root/.mm-claude/CLAUDE.md','w').write(CLAUDE_SYSTEM_PROMPT)" \
    && rm /tmp/system_prompt.py

# Create directories
RUN mkdir -p /workspace/gt /project

VOLUME /project
EXPOSE 18789

ENTRYPOINT ["gasclaw"]
CMD ["start"]
