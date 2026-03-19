FROM node:22-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# OpenCode
RUN curl -fsSL https://opencode.ai/install | bash || true

# Install mm CLI (for system prompt)
RUN pip install --no-cache-dir --break-system-packages minimax-agent || true

# Write instructions for OpenCode (read by opencode.json at launch time)
COPY src/minimax_cli/system_prompt.py /tmp/
RUN python3 -c "exec(open('/tmp/system_prompt.py').read()); open('/root/.opencode-instructions.md','w').write(SYSTEM_PROMPT)" \
    && rm /tmp/system_prompt.py

WORKDIR /app
ENTRYPOINT ["opencode"]
