FROM node:22-slim
RUN curl -fsSL https://opencode.ai/install | bash && \
    apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENTRYPOINT ["opencode"]
