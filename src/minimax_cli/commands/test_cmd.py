"""test command — run inference health checks."""

from __future__ import annotations

import subprocess

import click

from ..constants import SCRIPTS_DIR


@click.command("test")
def test():
    """Run inference health checks against the running server."""
    script = SCRIPTS_DIR / "test.sh"
    if not script.exists():
        click.echo(f"Script not found: {script}", err=True)
        raise SystemExit(1)
    subprocess.run(["bash", str(script)])
