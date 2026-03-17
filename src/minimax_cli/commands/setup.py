"""setup <tool> — configure AI coding tools to use MiniMax-M2.5."""

from __future__ import annotations

import json
import os
from pathlib import Path

import click
from rich.console import Console

from ..config import get_api_key
from ..constants import PUBLIC_API_BASE, DEFAULT_MODEL

console = Console()


def _require_key() -> str:
    key = get_api_key()
    if not key:
        console.print("[red]No API key found.[/] Run: mm auth login")
        raise SystemExit(1)
    return key


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def setup():
    """Configure AI coding tools to use MiniMax-M2.5."""


@setup.command()
@click.option("--write", is_flag=True, help="Append env vars to shell profile.")
def claude(write: bool):
    """Configure Claude Code to use MiniMax-M2.5."""
    key = _require_key()
    lines = [
        f'export ANTHROPIC_BASE_URL="{PUBLIC_API_BASE}"',
        f'export ANTHROPIC_API_KEY="{key}"',
    ]
    console.print("[bold]Claude Code — add to your shell profile:[/]\n")
    for line in lines:
        console.print(f"  {line}")
    console.print(f"\n  claude --model {DEFAULT_MODEL}")

    if write:
        _append_to_profile(lines, "Claude Code / MiniMax-M2.5")


@setup.command()
def codex():
    """Configure Codex CLI to use MiniMax-M2.5."""
    key = _require_key()
    config_dir = Path.home() / ".codex"
    config_file = config_dir / "config.yaml"

    content = (
        f"provider: openai\n"
        f"model: {DEFAULT_MODEL}\n"
        f"base_url: {PUBLIC_API_BASE}\n"
        f"api_key: {key}\n"
    )

    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.write_text(content)
    console.print(f"[green]Written:[/] {config_file}")
    console.print(f"\n  codex --model {DEFAULT_MODEL} \"your prompt\"")


@setup.command()
def openclaw():
    """Print OpenClaw provider config for MiniMax-M2.5."""
    key = _require_key()
    provider = {
        "id": "minimax",
        "name": "MiniMax-M2.5",
        "api": "openai-completions",
        "baseUrl": PUBLIC_API_BASE,
        "apiKey": key,
        "timeout": 600000,
        "models": [{
            "id": DEFAULT_MODEL,
            "name": "MiniMax-M2.5 (128K)",
            "contextWindow": 131072,
            "maxTokens": 131072,
        }],
    }
    console.print("[bold]OpenClaw — add to openclaw.json models.providers:[/]\n")
    console.print(json.dumps(provider, indent=2))
    console.print(f"\n  openclaw config set model \"minimax/{DEFAULT_MODEL}\"")


@setup.command()
def opencode():
    """Configure OpenCode to use MiniMax-M2.5."""
    key = _require_key()
    config_dir = Path.home() / ".opencode"
    config_file = config_dir / "config.json"

    config = {
        "provider": {
            "name": "openai-compatible",
            "apiBase": PUBLIC_API_BASE,
            "apiKey": key,
            "model": DEFAULT_MODEL,
        }
    }

    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.write_text(json.dumps(config, indent=2) + "\n")
    console.print(f"[green]Written:[/] {config_file}")


@setup.command()
def aider():
    """Configure Aider to use MiniMax-M2.5."""
    key = _require_key()
    config_file = Path.home() / ".aider.conf.yml"

    content = (
        f"openai-api-base: {PUBLIC_API_BASE}\n"
        f"openai-api-key: {key}\n"
        f"model: openai/{DEFAULT_MODEL}\n"
    )

    config_file.write_text(content)
    console.print(f"[green]Written:[/] {config_file}")
    console.print(f"\n  aider --model openai/{DEFAULT_MODEL}")


@setup.command("continue")
def continue_ide():
    """Configure Continue (VS Code / JetBrains) for MiniMax-M2.5."""
    key = _require_key()
    config_file = Path.home() / ".continue" / "config.json"

    model_entry = {
        "title": "MiniMax-M2.5",
        "provider": "openai",
        "model": DEFAULT_MODEL,
        "apiBase": PUBLIC_API_BASE,
        "apiKey": key,
    }

    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
        except json.JSONDecodeError:
            config = {}
    else:
        config = {}

    models = config.get("models", [])
    # Replace existing MiniMax entry or append
    models = [m for m in models if m.get("title") != "MiniMax-M2.5"]
    models.append(model_entry)
    config["models"] = models

    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(json.dumps(config, indent=2) + "\n")
    console.print(f"[green]Written:[/] {config_file}")


@setup.command()
def cline():
    """Print Cline (VS Code) setup instructions."""
    key = _require_key()
    console.print("[bold]Cline — VS Code Extension Setup[/]\n")
    console.print("1. Open Cline settings in VS Code")
    console.print('2. Set API Provider to [bold]"OpenAI Compatible"[/]')
    console.print(f"3. Base URL: [cyan]{PUBLIC_API_BASE}[/]")
    console.print(f"4. API Key: [dim]{key[:8]}...{key[-4:]}[/] (paste your full key)")
    console.print(f"5. Model ID: [cyan]{DEFAULT_MODEL}[/]")


def _append_to_profile(lines: list[str], label: str) -> None:
    """Append environment variables to the user's shell profile."""
    for rc in [Path.home() / ".bashrc", Path.home() / ".zshrc"]:
        if rc.exists():
            content = rc.read_text()
            marker = f"# {label}"
            if marker in content:
                console.print(f"[yellow]Already in {rc.name}[/]")
                continue
            with open(rc, "a") as f:
                f.write(f"\n{marker}\n")
                for line in lines:
                    f.write(line + "\n")
            console.print(f"[green]Appended to {rc.name}[/]")
