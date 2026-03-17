"""Nori TUI launcher — launches Nori with MiniMax API backend."""

import os
import shutil
import subprocess
import sys

import click

from ..config import get_api_key
from ..constants import PUBLIC_API_BASE


@click.command()
def term():
    """Launch Nori TUI with MiniMax-M2.5."""
    # Check if nori is installed
    nori_bin = shutil.which("nori")
    if not nori_bin:
        click.echo("Nori is not installed. Installing...")
        try:
            # Try npm first (nori is distributed via npm)
            npm_bin = shutil.which("npm")
            if not npm_bin:
                click.echo("npm not found. Install nori manually:")
                click.echo("  npm install -g nori-ai-cli")
                raise SystemExit(1)
            subprocess.run(
                [npm_bin, "install", "-g", "nori-ai-cli"],
                check=True,
            )
            nori_bin = shutil.which("nori")
            if not nori_bin:
                click.echo("nori installed but not found in PATH.")
                click.echo("Try: npm install -g nori-ai-cli")
                raise SystemExit(1)
        except subprocess.CalledProcessError:
            click.echo("Failed to install nori. Install manually:")
            click.echo("  npm install -g nori-ai-cli")
            raise SystemExit(1)

    # Install senior-swe skillset (shared with mm launch nori)
    from .launch import _ensure_senior_swe
    _ensure_senior_swe()

    # Get API key and set env vars for Claude Code backend
    key = get_api_key()
    env = os.environ.copy()
    if key:
        env["ANTHROPIC_BASE_URL"] = PUBLIC_API_BASE
        env["ANTHROPIC_API_KEY"] = key
        env["ANTHROPIC_AUTH_TOKEN"] = key

    click.echo("Launching Nori TUI...")
    os.execvpe(nori_bin, [nori_bin], env)
