"""auth login/status/logout — API key management."""

from __future__ import annotations

import click
from rich.console import Console

from ..config import get_api_key, save_api_key, delete_api_key
from ..api import verify_key

console = Console()


@click.group()
def auth():
    """Manage API key authentication."""


@auth.command()
@click.option("--key", "key_opt", default=None, help="API key (or omit to prompt).")
def login(key_opt: str | None):
    """Store an API key for accessing the MiniMax server."""
    if key_opt:
        key = key_opt.strip()
    else:
        key = click.prompt("API key", hide_input=True).strip()
    if not key:
        console.print("[red]Empty key.[/]")
        raise SystemExit(1)

    console.print("Verifying key...", end=" ")
    if verify_key(key):
        save_api_key(key)
        console.print("[green]valid![/]")
        console.print(f"Saved to ~/.config/minimax/config.json")
    else:
        console.print("[red]failed![/]")
        console.print("Could not verify against LiteLLM. Save anyway?")
        if click.confirm("Save key?", default=False):
            save_api_key(key)
            console.print("Saved.")
        else:
            console.print("Not saved.")


@auth.command()
def status():
    """Show current auth status and verify key."""
    key = get_api_key()
    if not key:
        console.print("[yellow]Not authenticated.[/] Run: minimax auth login")
        return

    masked = key[:8] + "..." + key[-4:] if len(key) > 12 else key[:4] + "..."
    console.print(f"Key: {masked}")

    if verify_key(key):
        console.print(f"Status: [green]valid[/]")
    else:
        console.print(f"Status: [red]could not verify[/] (server may be down)")


@auth.command()
def logout():
    """Remove stored API key."""
    key = get_api_key()
    if not key:
        console.print("[yellow]No stored key to remove.[/]")
        return
    delete_api_key()
    console.print("API key removed.")
