from __future__ import annotations
"""term — launch Toad TUI with MiniMax-M2.5 via ACP."""

import os
import shutil

import click
from rich.console import Console

from ..config import get_api_key

console = Console()


__all__ = ["cmd","term"]
@click.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def term(extra_args: tuple):
    """Launch Toad TUI with MiniMax-M2.5.

    Toad connects to MiniMax via the ACP (Agent Client Protocol) server,
    giving you a full terminal UI with tool execution (bash, file I/O, search).

    Requires: pip install batrachian-toad (Python 3.14+)
    """
    key = get_api_key()
    if not key:
        console.print("[red]No API key set.[/] Run: mm auth login")
        raise SystemExit(1)

    # Check if toad is installed
    toad_bin = shutil.which("toad")
    if not toad_bin:
        console.print("[red]toad not found.[/] Install it first:")
        console.print("  pip install batrachian-toad")
        console.print()
        console.print("[dim]Note: Toad requires Python 3.14+[/]")
        raise SystemExit(1)

    # Find mm binary for ACP backend
    mm_bin = shutil.which("mm") or shutil.which("minimax")
    if not mm_bin:
        console.print("[red]mm binary not found in PATH[/]")
        raise SystemExit(1)

    # Launch toad with MiniMax ACP backend
    args = [toad_bin, "acp", f"{mm_bin} acp", "-t", "MiniMax-M2.5"] + list(extra_args)
    console.print("[bold]Launching Toad[/] with MiniMax-M2.5 (via ACP)...")
    console.print()
    os.execvp(toad_bin, args)
