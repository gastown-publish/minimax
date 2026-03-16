"""Toad TUI launcher — launches Toad with MiniMax ACP backend."""

import click


@click.command()
def term():
    """Launch Toad TUI with MiniMax agent."""
    import shutil
    import subprocess
    import sys

    # Check if toad is installed
    toad_bin = shutil.which("toad")
    if not toad_bin:
        click.echo("Installing Toad...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "batrachian-toad"],
            check=True,
        )
        toad_bin = shutil.which("toad")
        if not toad_bin:
            click.echo("Failed to install Toad. Install manually: pip install batrachian-toad")
            raise SystemExit(1)

    # Find mm binary for ACP
    mm_bin = shutil.which("mm") or shutil.which("minimax")
    if not mm_bin:
        click.echo("Error: mm binary not found in PATH")
        raise SystemExit(1)

    # Launch toad with MiniMax ACP backend
    import os

    os.execvp(toad_bin, [toad_bin, "acp", f"{mm_bin} acp"])
