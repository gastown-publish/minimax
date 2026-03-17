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

    # Install nori-skillsets and senior-swe skillset if not present
    sks_bin = shutil.which("nori-skillsets")
    nori_profiles = os.path.expanduser("~/.nori/profiles")
    senior_swe_dir = os.path.join(nori_profiles, "senior-swe")

    if not os.path.isdir(senior_swe_dir):
        if not sks_bin:
            click.echo("Installing nori-skillsets...")
            npm_bin = shutil.which("npm")
            if npm_bin:
                subprocess.run(
                    [npm_bin, "install", "-g", "nori-skillsets"],
                    capture_output=True,
                )
                sks_bin = shutil.which("nori-skillsets")

        if sks_bin:
            click.echo("Installing senior-swe skillset...")
            subprocess.run(
                [sks_bin, "install", "senior-swe", "--non-interactive"],
                capture_output=True,
                timeout=30,
            )

    # Get API key and set env vars for Claude Code backend
    key = get_api_key()
    env = os.environ.copy()
    if key:
        env["ANTHROPIC_BASE_URL"] = PUBLIC_API_BASE
        env["ANTHROPIC_API_KEY"] = key
        env["ANTHROPIC_AUTH_TOKEN"] = key

    click.echo("Launching Nori TUI...")
    os.execvpe(nori_bin, [nori_bin], env)
