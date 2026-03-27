"""test command — run inference health checks."""

from __future__ import annotations

import subprocess

import click
from rich.console import Console

from ..config import get_api_key
from ..api import _base_url, check_health, list_models

console = Console()


__all__ = ["cmd","test"]
@click.command("test")
def test():
    """Run inference health checks against the API."""
    from ..constants import SCRIPTS_DIR

    # If on server with scripts, use the full test script
    if SCRIPTS_DIR.exists() and (SCRIPTS_DIR / "test.sh").exists():
        subprocess.run(["bash", str(SCRIPTS_DIR / "test.sh")])
        return

    # Client-side health check
    api_key = get_api_key()
    base = _base_url(api_key)

    console.print(f"[bold]Testing API connection...[/]")
    console.print(f"  Endpoint: {base}")

    if not api_key:
        console.print(f"  [yellow]No API key set.[/] Run: mm auth login")
        raise SystemExit(1)

    console.print(f"  Key: {api_key[:8]}...{api_key[-4:]}")

    # Health check
    healthy = check_health(api_key)
    if healthy:
        console.print(f"  Health: [green]OK[/]")
    else:
        console.print(f"  Health: [red]FAILED[/]")
        raise SystemExit(1)

    # Model listing
    models = list_models(api_key)
    if models:
        console.print(f"  Models: {len(models)} available")
        for m in models:
            console.print(f"    - {m.get('id', 'unknown')}")
    else:
        console.print(f"  Models: [yellow]none returned[/]")

    console.print(f"\n[green]All checks passed.[/]")
