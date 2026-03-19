FROM python:3.14-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl \
    && rm -rf /var/lib/apt/lists/*

# Toad + mm CLI (toad uses mm acp for MiniMax connection)
RUN pip install --no-cache-dir batrachian-toad minimax-agent

# Write system prompt for Toad
COPY src/minimax_cli/system_prompt.py /tmp/
RUN python3 -c "exec(open('/tmp/system_prompt.py').read()); open('/root/.toad-system-prompt.md','w').write(SYSTEM_PROMPT)" \
    && rm /tmp/system_prompt.py

WORKDIR /app
ENTRYPOINT ["toad"]
