FROM node:22-slim
RUN npm install -g nori-ai-cli @anthropic-ai/claude-code && \
    apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENTRYPOINT ["nori"]
