"""Shared constants for paths, URLs, and model IDs."""

import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
# Default to repo root, allow override via env var
_REPO_DEFAULT = Path(__file__).resolve().parents[2]
REPO_DIR = Path(os.environ.get("MINIMAX_REPO_DIR", _REPO_DEFAULT))
SCRIPTS_DIR = REPO_DIR / "scripts"

# Server-only paths — allow override via env vars
_SERVER_REPO_DEFAULT = os.environ.get("MINIMAX_SERVER_DIR", "/opt/minimax")
_SERVER_REPO = Path(_SERVER_REPO_DEFAULT)
VENV_DIR = _SERVER_REPO / ".venv" if _SERVER_REPO.exists() else None
_MODEL_DIR_DEFAULT = os.environ.get("MINIMAX_MODEL_DIR", "/opt/models/MiniMax-M2.5-HF")
MODEL_DIR = Path(_MODEL_DIR_DEFAULT) if Path(_MODEL_DIR_DEFAULT).exists() else None

CONFIG_DIR = Path.home() / ".config" / "minimax"
CONFIG_FILE = CONFIG_DIR / "config.json"
KEYS_FILE = CONFIG_DIR / "keys.json"

LITELLM_CONFIG = REPO_DIR / "litellm-config.yaml"

# ── PID files & logs ──────────────────────────────────────────────────
VLLM_PID = Path("/tmp/vllm-minimax.pid")
LITELLM_PID = Path("/tmp/litellm-minimax.pid")
VLLM_LOG = Path("/tmp/vllm-minimax.log")
LITELLM_LOG = Path("/tmp/litellm-minimax.log")

# ── URLs ──────────────────────────────────────────────────────────────
VLLM_BASE = "http://localhost:8080"
LITELLM_BASE = "http://localhost:4000"
PUBLIC_API_BASE = "https://api.minimax.villamarket.ai"
PUBLIC_API_V1 = "https://api.minimax.villamarket.ai/v1"
# Legacy alias — use PUBLIC_API_BASE for client-facing URLs
PUBLIC_BASE = PUBLIC_API_BASE + "/v1"

# ── Model IDs ─────────────────────────────────────────────────────────
MODEL_IDS = ["minimax-m2.5", "MiniMaxAI/MiniMax-M2.5"]
DEFAULT_MODEL = "minimax-m2.5"

# ── Context Windows ──────────────────────────────────────────────────
CONTEXT_WINDOW = 128_000  # Max input tokens
OUTPUT_WINDOW = 16_384   # Max output tokens
FULL_CONTEXT = 131_072  # Combined context window

# ── SES ───────────────────────────────────────────────────────────────
SES_SENDER = "noreply@villamarket.ai"
SES_REGION = "us-east-1"
