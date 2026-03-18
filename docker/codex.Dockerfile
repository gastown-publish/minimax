FROM node:22-slim
RUN npm install -g @openai/codex && \
    apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENTRYPOINT ["codex"]
