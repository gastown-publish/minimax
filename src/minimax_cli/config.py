"""Read/write ~/.config/minimax/config.json and keys.json."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

from .constants import CONFIG_DIR, CONFIG_FILE, KEYS_FILE


def _ensure_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _write_json(path: Path, data: dict) -> None:
    _ensure_dir()
    path.write_text(json.dumps(data, indent=2) + "\n")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600


# ── API key config ────────────────────────────────────────────────────

def get_api_key() -> str | None:
    """Return API key from env var or config file."""
    key = os.environ.get("MINIMAX_API_KEY")
    if key:
        return key
    cfg = _read_json(CONFIG_FILE)
    return cfg.get("api_key")


def save_api_key(key: str) -> None:
    cfg = _read_json(CONFIG_FILE)
    cfg["api_key"] = key
    _write_json(CONFIG_FILE, cfg)


def delete_api_key() -> None:
    cfg = _read_json(CONFIG_FILE)
    cfg.pop("api_key", None)
    _write_json(CONFIG_FILE, cfg)


def get_litellm_master_key() -> str | None:
    """Extract master_key from litellm-config.yaml."""
    from .constants import LITELLM_CONFIG
    key = os.environ.get("LITELLM_MASTER_KEY")
    if key:
        return key
    if LITELLM_CONFIG.exists():
        for line in LITELLM_CONFIG.read_text().splitlines():
            if "master_key:" in line:
                return line.split(":", 1)[1].strip().strip('"').strip("'")
    return None


# ── Persistent key store ──────────────────────────────────────────────

def load_keys() -> dict:
    """Load persistent key store: {token_hash: {key, alias, email, created_at}}."""
    return _read_json(KEYS_FILE)


def save_key_entry(token_hash: str, full_key: str, alias: str = "",
                   email: str = "", created_at: str = "") -> None:
    """Save a generated key to the persistent store."""
    keys = load_keys()
    keys[token_hash] = {
        "key": full_key,
        "alias": alias,
        "email": email,
        "created_at": created_at,
    }
    _write_json(KEYS_FILE, keys)


def get_full_key(token_hash: str) -> str | None:
    """Retrieve a full key by its token hash."""
    keys = load_keys()
    entry = keys.get(token_hash)
    return entry["key"] if entry else None


def delete_key_entry(token_hash: str) -> None:
    """Remove a key from the persistent store."""
    keys = load_keys()
    keys.pop(token_hash, None)
    _write_json(KEYS_FILE, keys)
