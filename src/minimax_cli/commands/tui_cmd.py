"""tui command — launch the admin TUI for key management."""

from __future__ import annotations

import os
import sys

import click

from ..constants import REPO_DIR
from ..config import get_litellm_master_key


@click.command("tui")
def tui():
    """Launch the admin TUI for API key management."""
    # Ensure LITELLM_MASTER_KEY is set
    if not os.environ.get("LITELLM_MASTER_KEY"):
        master_key = get_litellm_master_key()
        if master_key:
            os.environ["LITELLM_MASTER_KEY"] = master_key
        else:
            click.echo("Warning: LITELLM_MASTER_KEY not found. Set it or create litellm-config.yaml.", err=True)

    # Add repo to path so tui module is importable
    repo_str = str(REPO_DIR)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)

    try:
        from tui.app import MiniMaxAdmin
        app = MiniMaxAdmin()
        app.run()
    except ImportError as e:
        click.echo(f"TUI dependencies missing: {e}", err=True)
        click.echo("Install with: pip install 'minimax-cli[tui]'")
        raise SystemExit(1)
