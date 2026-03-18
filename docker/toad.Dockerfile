FROM python:3.14-slim
RUN pip install --no-cache-dir batrachian-toad minimax-agent && \
    apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENTRYPOINT ["toad"]
