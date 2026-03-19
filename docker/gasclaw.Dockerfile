# Gasclaw Docker image — built from gasclaw repo
# This is a thin wrapper that clones and builds gasclaw with MiniMax support
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

# Claude Code + OpenClaw + Kimi CLI
RUN npm install -g @anthropic-ai/claude-code openclaw
RUN pip install --no-cache-dir kimi-cli minimax-agent

# Gastown + Beads
RUN go install github.com/steveyegge/gastown/cmd/gt@v0.10.0 || true
RUN go install github.com/steveyegge/beads/cmd/bd@latest || true

# AIS session manager
RUN curl -sL https://raw.githubusercontent.com/gastown-publish/ais/main/bin/ais \
    -o /usr/local/bin/ais && chmod +x /usr/local/bin/ais || true

# Install gasclaw from GitHub
RUN pip install --no-cache-dir git+https://github.com/gastown-publish/gasclaw.git || true

# Create directories
RUN mkdir -p /workspace/gt /project

VOLUME /project
EXPOSE 18789

ENTRYPOINT ["gasclaw"]
CMD ["start"]
