"""Shared constants for paths, URLs, and model IDs."""

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
REPO_DIR = Path(__file__).resolve().parents[2]  # /home/nic/data/models/MiniMax-M2.5
SCRIPTS_DIR = REPO_DIR / "scripts"
VENV_DIR = Path("/home/nic/data/models/MiniMax-M2.5/.venv")
MODEL_DIR = Path("/home/nic/data/models/MiniMax-M2.5-HF")

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
PUBLIC_BASE = "https://gpu-workspace.taile8dc37.ts.net/minimax/v1"

# ── Model IDs ─────────────────────────────────────────────────────────
MODEL_IDS = ["minimax-m2.5", "MiniMaxAI/MiniMax-M2.5"]
DEFAULT_MODEL = "minimax-m2.5"

# ── SES ───────────────────────────────────────────────────────────────
SES_SENDER = "noreply@villamarket.ai"
SES_REGION = "us-east-1"
