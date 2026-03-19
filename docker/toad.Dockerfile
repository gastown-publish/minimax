# Toad — full-featured AI agent TUI with all tools pre-installed
# Toad manages agents via ACP, so it needs Claude Code + full toolchain inside
FROM python:3.14-slim

ARG TARGETARCH=amd64

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates gnupg xclip build-essential \
    && rm -rf /var/lib/apt/lists/*

# Node.js 22 (for Claude Code, Nori, nori-skillsets, Playwright MCP)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Claude Code + Nori + Nori skillsets
RUN npm install -g @anthropic-ai/claude-code nori-ai-cli nori-skillsets

# Playwright MCP plugin (browser testing for agents)
RUN npx -y @anthropic-ai/claude-code mcp add playwright -- npx @anthropic-ai/mcp-server-playwright 2>/dev/null || true

# Install nori senior-swe skillset (17 skills for Claude Code)
RUN nori-skillsets install senior-swe --non-interactive 2>/dev/null || true

# Toad + mm CLI
RUN pip install --no-cache-dir --break-system-packages batrachian-toad minimax-agent

# Copy bundled skills into Claude Code's global skills dir
COPY src/minimax_cli/skills/*.md /root/.claude/skills/

# Copy skills + system prompt into mm-claude config
RUN mkdir -p /root/.mm-claude/skills
COPY src/minimax_cli/skills/*.md /root/.mm-claude/skills/
COPY src/minimax_cli/system_prompt.py /tmp/
RUN python3 -c "exec(open('/tmp/system_prompt.py').read()); open('/root/.mm-claude/CLAUDE.md','w').write(CLAUDE_SYSTEM_PROMPT)" \
    && python3 -c "exec(open('/tmp/system_prompt.py').read()); open('/root/.toad-system-prompt.md','w').write(SYSTEM_PROMPT)" \
    && rm /tmp/system_prompt.py

# XDG directories for Toad config persistence
ENV XDG_CONFIG_HOME=/root/.config
ENV XDG_DATA_HOME=/root/.local/share
ENV XDG_STATE_HOME=/root/.local/state
RUN mkdir -p /root/.config/toad /root/.local/share/toad /root/.local/state/toad

# Terminal support
ENV TERM=xterm-256color
ENV COLORTERM=truecolor

WORKDIR /app
ENTRYPOINT ["toad"]
