"""launch <tool> — launch AI coding tools pre-configured for MiniMax-M2.5."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

import click
from rich.console import Console

from ..config import get_api_key
from ..constants import PUBLIC_API_BASE, PUBLIC_API_V1, DEFAULT_MODEL

console = Console()


def _require_key() -> str:
    key = get_api_key()
    if not key:
        console.print("[red]No API key set.[/] Run: mm auth login")
        raise SystemExit(1)
    return key


def _require_binary(name: str, install_hint: str) -> str:
    """Find a binary or show install instructions."""
    path = shutil.which(name)
    if not path:
        console.print(f"[red]{name} not found.[/] Install it first:")
        console.print(f"  {install_hint}")
        raise SystemExit(1)
    return path


@click.group()
def launch():
    """Launch AI coding tools with MiniMax-M2.5.

    Example:
        mm launch claude
        mm launch aider
        mm launch codex
        mm launch opencode
    """


@launch.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def claude(extra_args: tuple):
    """Launch Claude Code with MiniMax-M2.5."""
    key = _require_key()
    binary = _require_binary("claude", "npm install -g @anthropic-ai/claude-code")

    env = os.environ.copy()
    # Claude Code uses ANTHROPIC_BASE_URL for API endpoint
    # and sends x-api-key header from ANTHROPIC_API_KEY
    env["ANTHROPIC_BASE_URL"] = PUBLIC_API_BASE
    env["ANTHROPIC_API_KEY"] = key
    # Some versions also check ANTHROPIC_AUTH_TOKEN
    env["ANTHROPIC_AUTH_TOKEN"] = key

    args = [binary, "--model", DEFAULT_MODEL] + list(extra_args)
    console.print(f"[bold]Launching Claude Code[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_BASE}")
    console.print(f"  Model: {DEFAULT_MODEL}")
    console.print()
    os.execvpe(binary, args, env)


@launch.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def aider(extra_args: tuple):
    """Launch Aider with MiniMax-M2.5."""
    key = _require_key()
    binary = _require_binary("aider", "pip install aider-chat")

    env = os.environ.copy()
    # Aider uses OPENAI_API_BASE (with /v1 suffix)
    env["OPENAI_API_BASE"] = PUBLIC_API_V1
    env["OPENAI_API_KEY"] = key

    args = [binary, "--model", f"openai/{DEFAULT_MODEL}"] + list(extra_args)
    console.print(f"[bold]Launching Aider[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_V1}")
    console.print(f"  Model: openai/{DEFAULT_MODEL}")
    console.print()
    os.execvpe(binary, args, env)


@launch.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def codex(extra_args: tuple):
    """Launch Codex CLI with MiniMax-M2.5."""
    key = _require_key()
    binary = _require_binary("codex", "npm install -g @openai/codex")

    env = os.environ.copy()
    # Codex uses OPENAI_BASE_URL (without /v1 — it appends it)
    env["OPENAI_BASE_URL"] = PUBLIC_API_V1
    env["OPENAI_API_KEY"] = key

    args = [binary, "--model", DEFAULT_MODEL] + list(extra_args)
    console.print(f"[bold]Launching Codex[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_V1}")
    console.print(f"  Model: {DEFAULT_MODEL}")
    console.print()
    os.execvpe(binary, args, env)


@launch.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def opencode(extra_args: tuple):
    """Launch OpenCode with MiniMax-M2.5."""
    key = _require_key()
    binary = _require_binary("opencode", "go install github.com/opencode-ai/opencode@latest")

    env = os.environ.copy()
    # OpenCode uses OPENAI_BASE_URL and OPENAI_API_KEY
    env["OPENAI_BASE_URL"] = PUBLIC_API_V1
    env["OPENAI_API_KEY"] = key

    args = [binary] + list(extra_args)
    console.print(f"[bold]Launching OpenCode[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_V1}")
    console.print()
    os.execvpe(binary, args, env)


@launch.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def openclaw(extra_args: tuple):
    """Launch OpenClaw with MiniMax-M2.5."""
    key = _require_key()
    binary = _require_binary("openclaw", "pip install openclaw-cli")

    env = os.environ.copy()
    # OpenClaw uses OPENAI_API_BASE (with /v1)
    env["OPENAI_API_BASE"] = PUBLIC_API_V1
    env["OPENAI_API_KEY"] = key

    args = [binary, "--model", f"minimax/{DEFAULT_MODEL}"] + list(extra_args)
    console.print(f"[bold]Launching OpenClaw[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_V1}")
    console.print(f"  Model: minimax/{DEFAULT_MODEL}")
    console.print()
    os.execvpe(binary, args, env)


@launch.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def nori(extra_args: tuple):
    """Launch Nori TUI with MiniMax-M2.5."""
    key = _require_key()
    binary = _require_binary("nori", "npm install -g nori-ai-cli")

    env = os.environ.copy()
    # Nori wraps Claude Code — set Anthropic env vars for MiniMax API
    env["ANTHROPIC_BASE_URL"] = PUBLIC_API_BASE
    env["ANTHROPIC_API_KEY"] = key
    env["ANTHROPIC_AUTH_TOKEN"] = key

    args = [binary] + list(extra_args)
    console.print(f"[bold]Launching Nori[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_BASE}")
    console.print()
    os.execvpe(binary, args, env)
