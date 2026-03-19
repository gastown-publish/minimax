FROM node:22-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Codex CLI
RUN npm install -g @openai/codex

# Install mm CLI (for system prompt / instructions)
RUN pip install --no-cache-dir --break-system-packages minimax-agent || true

# Write instructions file for Codex
RUN mkdir -p /root/.codex
COPY src/minimax_cli/system_prompt.py /tmp/
RUN python3 -c "exec(open('/tmp/system_prompt.py').read()); open('/root/.codex/instructions.md','w').write(SYSTEM_PROMPT)" \
    && rm /tmp/system_prompt.py

WORKDIR /app
ENTRYPOINT ["codex"]
