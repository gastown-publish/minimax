from __future__ import annotations
"""ACP server command — exposes MiniMax-M2.5 to Toad and IDEs."""

import asyncio

import click


__all__ = ["cmd", "acp"]
@click.command("acp")
def acp():
    """Start ACP server (for Toad and IDE integration)."""
    from ..acp.server import main

    asyncio.run(main())
