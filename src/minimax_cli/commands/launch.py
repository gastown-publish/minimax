"""launch <tool> — launch AI coding tools pre-configured for MiniMax-M2.5."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console

from ..config import get_api_key
from ..constants import PUBLIC_API_BASE, PUBLIC_API_V1, DEFAULT_MODEL

console = Console()

# Isolated config dir for mm-launched Claude Code (separate from normal claude)
MM_CLAUDE_CONFIG = os.path.expanduser("~/.mm-claude")

# Docker images for tools that support them
DOCKER_IMAGES = {
    "aider": "paulgauthier/aider",
    "openclaw": "ghcr.io/openclaw/openclaw:latest",
}


def _require_key() -> str:
    key = get_api_key()
    if not key:
        console.print("[red]No API key set.[/] Run: mm auth login")
        raise SystemExit(1)
    return key


def _has_docker() -> bool:
    """Check if Docker is available."""
    return shutil.which("docker") is not None


def _docker_run(image: str, env: dict[str, str], extra_args: tuple = (),
                volumes: list[str] | None = None, interactive: bool = True):
    """Run a tool via Docker."""
    cmd = ["docker", "run", "--rm"]
    if interactive:
        cmd += ["-it"]
    # Mount current directory as workspace
    cwd = os.getcwd()
    cmd += ["-v", f"{cwd}:/app", "-w", "/app"]
    # Mount home config dirs
    home = str(Path.home())
    cmd += ["-v", f"{home}/.gitconfig:/root/.gitconfig:ro"]
    if os.path.exists(f"{home}/.ssh"):
        cmd += ["-v", f"{home}/.ssh:/root/.ssh:ro"]
    # Extra volumes
    for v in (volumes or []):
        cmd += ["-v", v]
    # Environment variables
    for k, v in env.items():
        cmd += ["-e", f"{k}={v}"]
    cmd.append(image)
    cmd.extend(extra_args)

    console.print(f"  [dim]Docker: {image}[/]")
    console.print()
    os.execvp("docker", cmd)


def _find_binary(name: str) -> str | None:
    """Find a binary, return None if not found."""
    return shutil.which(name)


def _require_binary(name: str, install_hint: str) -> str:
    """Find a binary or show install instructions."""
    path = shutil.which(name)
    if not path:
        console.print(f"[red]{name} not found.[/] Install it first:")
        console.print(f"  {install_hint}")
        raise SystemExit(1)
    return path


def _ensure_senior_swe():
    """Install nori-skillsets + senior-swe skillset if not present."""
    nori_profiles = os.path.expanduser("~/.nori/profiles")
    senior_swe_dir = os.path.join(nori_profiles, "senior-swe")
    if os.path.isdir(senior_swe_dir):
        return

    sks_bin = shutil.which("nori-skillsets")
    if not sks_bin:
        npm_bin = shutil.which("npm")
        if npm_bin:
            console.print("Installing nori-skillsets...")
            subprocess.run(
                [npm_bin, "install", "-g", "nori-skillsets"],
                capture_output=True,
            )
            sks_bin = shutil.which("nori-skillsets")

    if sks_bin:
        console.print("Installing senior-swe skillset...")
        subprocess.run(
            [sks_bin, "install", "senior-swe", "--non-interactive"],
            capture_output=True,
            timeout=30,
        )


def _write_codex_config(key: str):
    """Write Codex config file so it skips the login screen."""
    config_dir = Path.home() / ".codex"
    config_file = config_dir / "config.yaml"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.write_text(
        f"provider: openai\n"
        f"model: {DEFAULT_MODEL}\n"
        f"base_url: {PUBLIC_API_V1}\n"
        f"api_key: {key}\n"
    )


def _write_opencode_config(key: str):
    """Write OpenCode config file."""
    config_dir = Path.home() / ".opencode"
    config_file = config_dir / "config.json"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.write_text(json.dumps({
        "provider": {
            "name": "openai-compatible",
            "apiBase": PUBLIC_API_V1,
            "apiKey": key,
            "model": DEFAULT_MODEL,
        }
    }, indent=2) + "\n")


def _write_aider_config(key: str):
    """Write Aider config file."""
    config_file = Path.home() / ".aider.conf.yml"
    config_file.write_text(
        f"openai-api-base: {PUBLIC_API_V1}\n"
        f"openai-api-key: {key}\n"
        f"model: openai/{DEFAULT_MODEL}\n"
    )


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def launch():
    """Launch AI coding tools with MiniMax-M2.5.

    Each tool is configured with your MiniMax API key and
    launches with the correct endpoint and model settings.
    Uses Docker when available, falls back to local install.

    \b
    Tools:
        mm launch claude     # Claude Code (isolated config)
        mm launch codex      # Codex CLI
        mm launch aider      # Aider (Docker or local)
        mm launch nori       # Nori TUI (wraps Claude Code)
        mm launch toad       # Toad TUI (via ACP, with tools)
        mm launch kimi       # Kimi CLI
        mm launch openclaw   # OpenClaw (Docker or local)
        mm launch opencode   # OpenCode
    """


@launch.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def claude(extra_args: tuple):
    """Launch Claude Code with MiniMax-M2.5 (isolated config).

    Uses an Anthropic-compatible translation layer so Claude Code
    can talk to MiniMax's API. Config is isolated from your normal
    Claude Code installation.
    """
    key = _require_key()
    binary = _require_binary("claude", "npm install -g @anthropic-ai/claude-code")

    env = os.environ.copy()
    # Claude Code uses ANTHROPIC_BASE_URL — LiteLLM translates at /v1/messages
    env["ANTHROPIC_BASE_URL"] = PUBLIC_API_BASE
    env["ANTHROPIC_API_KEY"] = key
    env["ANTHROPIC_AUTH_TOKEN"] = key
    # Set model via env var so Claude Code uses the right model
    env["CLAUDE_MODEL"] = DEFAULT_MODEL
    # Use separate config dir so normal 'claude' is unaffected
    env["CLAUDE_CONFIG_DIR"] = MM_CLAUDE_CONFIG

    args = [binary, "--model", DEFAULT_MODEL] + list(extra_args)
    console.print(f"[bold]Launching Claude Code[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_BASE}")
    console.print(f"  Model: {DEFAULT_MODEL}")
    console.print(f"  Config: {MM_CLAUDE_CONFIG}")
    console.print()
    os.execvpe(binary, args, env)


@launch.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def aider(extra_args: tuple):
    """Launch Aider with MiniMax-M2.5.

    Uses Docker (paulgauthier/aider) if available, otherwise local install.
    """
    key = _require_key()

    console.print(f"[bold]Launching Aider[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_V1}")
    console.print(f"  Model: openai/{DEFAULT_MODEL}")

    docker_env = {
        "OPENAI_API_BASE": PUBLIC_API_V1,
        "OPENAI_API_KEY": key,
    }
    docker_args = ("--model", f"openai/{DEFAULT_MODEL}") + extra_args

    if _has_docker():
        _docker_run(DOCKER_IMAGES["aider"], docker_env, docker_args)
    else:
        binary = _require_binary("aider", "pip install aider-chat")
        _write_aider_config(key)

        env = os.environ.copy()
        env.update(docker_env)

        args = [binary, "--model", f"openai/{DEFAULT_MODEL}"] + list(extra_args)
        console.print()
        os.execvpe(binary, args, env)


@launch.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def codex(extra_args: tuple):
    """Launch Codex CLI with MiniMax-M2.5."""
    key = _require_key()
    binary = _require_binary("codex", "npm install -g @openai/codex")

    # Write config file so Codex skips the login screen
    _write_codex_config(key)

    env = os.environ.copy()
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

    # Write config file for OpenCode
    _write_opencode_config(key)

    env = os.environ.copy()
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
    """Launch OpenClaw with MiniMax-M2.5.

    Uses Docker (ghcr.io/openclaw/openclaw) if available, otherwise local install.
    Runs 'openclaw agent' for an interactive agent session.
    """
    key = _require_key()

    console.print(f"[bold]Launching OpenClaw[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_V1}")
    console.print(f"  Model: minimax/{DEFAULT_MODEL}")

    oc_env = {
        "OPENAI_API_BASE": PUBLIC_API_V1,
        "OPENAI_API_KEY": key,
        "OPENAI_MODEL": f"minimax/{DEFAULT_MODEL}",
    }

    if _has_docker() and not _find_binary("openclaw"):
        # Docker: run openclaw agent with MiniMax
        home = str(Path.home())
        volumes = [f"{home}/.openclaw:/root/.openclaw"]
        docker_args = extra_args if extra_args else ("agent",)
        _docker_run(DOCKER_IMAGES["openclaw"], oc_env, docker_args, volumes=volumes)
    else:
        binary = _require_binary("openclaw", "pip install openclaw-cli")

        env = os.environ.copy()
        env.update(oc_env)

        # Default to 'agent' subcommand if no args given
        if extra_args:
            args = [binary] + list(extra_args)
        else:
            args = [binary, "agent"]
        console.print()
        os.execvpe(binary, args, env)


@launch.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def nori(extra_args: tuple):
    """Launch Nori TUI with MiniMax-M2.5.

    Nori wraps Claude Code. MiniMax API provides an Anthropic-compatible
    translation layer so Nori works seamlessly.
    """
    key = _require_key()
    binary = _require_binary("nori", "npm install -g nori-ai-cli")

    # Ensure senior-swe skillset is installed
    _ensure_senior_swe()

    env = os.environ.copy()
    # Nori wraps Claude Code — set Anthropic env vars for MiniMax API
    env["ANTHROPIC_BASE_URL"] = PUBLIC_API_BASE
    env["ANTHROPIC_API_KEY"] = key
    env["ANTHROPIC_AUTH_TOKEN"] = key
    # Set model so Claude Code underneath uses the right model
    env["CLAUDE_MODEL"] = DEFAULT_MODEL
    # Isolated config so normal claude is unaffected
    env["CLAUDE_CONFIG_DIR"] = MM_CLAUDE_CONFIG

    args = [binary] + list(extra_args)
    console.print(f"[bold]Launching Nori[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_BASE}")
    console.print(f"  Model: {DEFAULT_MODEL}")
    console.print()
    os.execvpe(binary, args, env)


@launch.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def toad(extra_args: tuple):
    """Launch Toad TUI with MiniMax-M2.5 (via ACP)."""
    _require_key()
    binary = _require_binary("toad", "pip install batrachian-toad")

    # Find mm binary for ACP backend
    mm_bin = shutil.which("mm") or shutil.which("minimax")
    if not mm_bin:
        console.print("[red]mm binary not found in PATH[/]")
        raise SystemExit(1)

    # Toad connects to MiniMax via our ACP server
    args = [binary, "acp", f"{mm_bin} acp", "-t", "MiniMax-M2.5"] + list(extra_args)
    console.print(f"[bold]Launching Toad[/] with MiniMax-M2.5 (via ACP)...")
    console.print()
    os.execvp(binary, args)


@launch.command()
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def kimi(extra_args: tuple):
    """Launch Kimi CLI with MiniMax-M2.5."""
    key = _require_key()
    binary = _require_binary("kimi", "pip install kimi-cli")

    env = os.environ.copy()
    # Kimi CLI uses OpenAI-compatible API
    env["OPENAI_BASE_URL"] = PUBLIC_API_V1
    env["OPENAI_API_KEY"] = key

    args = [binary, "--model", DEFAULT_MODEL] + list(extra_args)
    console.print(f"[bold]Launching Kimi CLI[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_V1}")
    console.print(f"  Model: {DEFAULT_MODEL}")
    console.print()
    os.execvpe(binary, args, env)
