"""Skills command — list and run bundled prompt templates."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

console = Console()


__all__ = ["skills","list_skills","run_skill"]
@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def skills():
    """Manage and run bundled skills."""


@skills.command("list")
def list_skills():
    """List available skills."""
    from ..skills import list_skills as _list

    all_skills = _list()
    if not all_skills:
        console.print("[dim]No skills found.[/]")
        return

    table = Table(title="Bundled Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Title", style="bold")
    table.add_column("Description")

    for s in all_skills:
        table.add_row(s["name"], s["title"], s["description"])

    console.print(table)


@skills.command("run")
@click.argument("name")
@click.argument("args", nargs=-1)
def run_skill(name: str, args: tuple):
    """Run a skill by name.

    Example:
        mm skills run deep-research "quantum computing"
    """
    from openai import OpenAI

    from ..api import _base_url
    from ..config import get_api_key
    from ..constants import DEFAULT_MODEL
    from ..skills import load_skill

    template = load_skill(name)
    if not template:
        console.print(f"[red]Unknown skill: {name}[/]")
        console.print("Run [cyan]mm skills list[/] to see available skills.")
        raise SystemExit(1)

    user_input = " ".join(args) if args else ""
    if not user_input:
        user_input = click.prompt("Enter input for the skill")

    api_key = get_api_key()
    base = _base_url(api_key)
    client = OpenAI(base_url=f"{base}/v1", api_key=api_key or "none")

    messages = [
        {"role": "system", "content": template},
        {"role": "user", "content": user_input},
    ]

    console.print(f"[bold]Running skill:[/] {name}")
    console.print()

    try:
        stream = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            max_tokens=8192,
            temperature=0.6,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                console.print(delta.content, end="", highlight=False)

        console.print()
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted.[/]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/]")
