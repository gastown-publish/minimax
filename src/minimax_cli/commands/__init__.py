from __future__ import annotations
__all__ = ["console", "ensure_api_key", "warn_no_api_key", "API_KEY_ENV", "DEFAULT_MODEL"]

"""Shared utilities for minimax CLI commands.

This module provides common utilities used across CLI commands:
- console: Shared Rich console instance
- ensure_api_key(): Validates API key is set, raises if not
- warn_no_api_key(): Prints warning when API key is missing
"""

import click
from rich.console import Console

from minimax_cli.config import get_api_key

console = Console()


def ensure_api_key() -> str:
    """Ensure API key is set, raise ClickException if not."""
    key = get_api_key()
    if not key:
        raise click.exceptions.ClickException(
            "No API key set. Run: mm auth login"
        )
    return key


def warn_no_api_key():
    """Print warning when API key is not set."""
    console.print("[red]No API key set.[/] Run: mm auth login")


# Note: This module also re-exports all commands for convenience
# from .auth import auth
# from .run import run
# etc.