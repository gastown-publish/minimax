"""tui command — launch the admin TUI for key management."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click

from ..config import get_litellm_master_key


def _find_repo_dir() -> Path | None:
    """Find the repo root by looking for tui/ directory up from source file."""
    # When installed from repo (pip install -e .), walk up parents
    for depth in [3, 4, 5]:
        try:
            candidate = Path(__file__).resolve().parents[depth]
        except IndexError:
            break
        if (candidate / "tui" / "app.py").exists():
            return candidate
    return None


@click.command("tui")
def tui():
    """Launch the admin TUI for API key management.

    This is an admin feature for self-hosted MiniMax servers.
    Requires the full repo checkout (not available via pip install).
    """
    repo_dir = _find_repo_dir()
    if repo_dir is None:
        click.echo("The TUI is an admin tool for self-hosted MiniMax servers.", err=True)
        click.echo("It requires the full server installation (not available via pip).", err=True)
        click.echo("", err=True)
        click.echo("For API key management, use the web dashboard:", err=True)
        click.echo("  https://minimax.villamarket.ai/dashboard", err=True)
        raise SystemExit(1)

    # Ensure LITELLM_MASTER_KEY is set
    if not os.environ.get("LITELLM_MASTER_KEY"):
        master_key = get_litellm_master_key()
        if master_key:
            os.environ["LITELLM_MASTER_KEY"] = master_key
        else:
            click.echo("Warning: LITELLM_MASTER_KEY not found. Set it or create litellm-config.yaml.", err=True)

    # Add repo to path so tui module is importable
    repo_str = str(repo_dir)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)

    try:
        from tui.app import MiniMaxAdmin
        app = MiniMaxAdmin()
        app.run()
    except ImportError as e:
        click.echo(f"TUI dependencies missing: {e}", err=True)
        click.echo("Install with: pip install 'minimax-agent[tui]'")
        raise SystemExit(1)
