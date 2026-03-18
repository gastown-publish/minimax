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
    "claude": "ghcr.io/gastown-publish/mm-claude:latest",
    "opencode": "ghcr.io/anomalyco/opencode:latest",
    "codex": "ghcr.io/gastown-publish/mm-codex:latest",
    "nori": "ghcr.io/gastown-publish/mm-nori:latest",
    "kimi": "ghcr.io/gastown-publish/mm-kimi:latest",
    "toad": "ghcr.io/gastown-publish/mm-toad:latest",
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
                volumes: list[str] | None = None, interactive: bool = True,
                run_as_host_user: bool = False):
    """Run a tool via Docker."""
    cmd = ["docker", "run", "--rm"]
    if interactive:
        cmd += ["-it"]
    if run_as_host_user:
        cmd += ["--user", f"{os.getuid()}:{os.getgid()}"]
    # Mount current directory as workspace
    cwd = os.getcwd()
    cmd += ["-v", f"{cwd}:/app", "-w", "/app"]
    # Mount home config dirs
    home = str(Path.home())
    if os.path.exists(f"{home}/.gitconfig"):
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


def _write_opencode_config(key: str, cwd: str | None = None):
    """Write OpenCode project config (opencode.json) in cwd."""
    target = Path(cwd or os.getcwd()) / "opencode.json"
    target.write_text(json.dumps({
        "$schema": "https://opencode.ai/config.json",
        "provider": {
            "minimax": {
                "npm": "@ai-sdk/openai-compatible",
                "name": "MiniMax",
                "options": {
                    "baseURL": PUBLIC_API_V1,
                    "apiKey": "{env:OPENAI_API_KEY}",
                },
                "models": {
                    DEFAULT_MODEL: {
                        "name": "MiniMax-M2.5",
                    }
                },
            }
        },
    }, indent=2) + "\n")


def _write_aider_config(key: str):
    """Write Aider config file."""
    config_file = Path.home() / ".aider.conf.yml"
    config_file.write_text(
        f"openai-api-base: {PUBLIC_API_V1}\n"
        f"openai-api-key: {key}\n"
        f"model: openai/{DEFAULT_MODEL}\n"
    )


def _write_kimi_config(key: str):
    """Write Kimi CLI config with MiniMax provider."""
    config_dir = Path.home() / ".kimi"
    config_file = config_dir / "config.toml"
    config_dir.mkdir(parents=True, exist_ok=True)

    # Only write if no config exists, or patch existing
    config = (
        f'default_model = "{DEFAULT_MODEL}"\n'
        f'default_thinking = true\n'
        f'\n'
        f'[models."{DEFAULT_MODEL}"]\n'
        f'provider = "minimax"\n'
        f'model = "{DEFAULT_MODEL}"\n'
        f'max_context_size = 131072\n'
        f'capabilities = ["thinking"]\n'
        f'\n'
        f'[providers."minimax"]\n'
        f'type = "openai_legacy"\n'
        f'base_url = "{PUBLIC_API_V1}"\n'
        f'api_key = "{key}"\n'
    )
    config_file.write_text(config)


def _ensure_claude_skills():
    """Copy bundled skills + Nori skills into Claude Code's skills dirs.

    Claude Code reads skills from ~/.claude/skills/ (global)
    and .claude/skills/ (project). We write to the global dir.
    """
    from ..skills import SKILLS_DIR

    # Claude Code always uses ~/.claude/skills/ regardless of CLAUDE_CONFIG_DIR
    target_dir = Path.home() / ".claude" / "skills"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy bundled skills
    for skill_file in SKILLS_DIR.glob("*.md"):
        dest = target_dir / skill_file.name
        if not dest.exists() or dest.read_text() != skill_file.read_text():
            dest.write_text(skill_file.read_text())

    # Copy Nori skills if available
    nori_skills_dir = Path.home() / ".nori" / "profiles" / "senior-swe" / "skills"
    if nori_skills_dir.is_dir():
        nori_target = target_dir / "nori"
        nori_target.mkdir(parents=True, exist_ok=True)
        for skill_dir in nori_skills_dir.iterdir():
            if skill_dir.is_dir():
                # Nori skills use SKILL.md
                for md_name in ("SKILL.md", "prompt.md"):
                    md_file = skill_dir / md_name
                    if md_file.exists():
                        dest = nori_target / f"{skill_dir.name}.md"
                        content = md_file.read_text()
                        if not dest.exists() or dest.read_text() != content:
                            dest.write_text(content)
                        break


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
@click.option("--no-docker", is_flag=True, help="Skip Docker, require local binary.")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def claude(no_docker: bool, extra_args: tuple):
    """Launch Claude Code with MiniMax-M2.5 (isolated config).

    Uses Docker if available, otherwise local install.
    Config is isolated from your normal Claude Code installation.
    Skills (Ralph Loop, code review, etc.) are auto-installed.
    """
    key = _require_key()

    # Copy skills into Claude Code config dir so /skills finds them
    _ensure_claude_skills()

    docker_env = {
        "ANTHROPIC_BASE_URL": PUBLIC_API_BASE,
        "ANTHROPIC_API_KEY": key,
        "CLAUDE_MODEL": DEFAULT_MODEL,
        "CLAUDE_CONFIG_DIR": "/root/.mm-claude",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    }
    docker_args = ("--model", DEFAULT_MODEL) + extra_args

    console.print(f"[bold]Launching Claude Code[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_BASE}")
    console.print(f"  Model: {DEFAULT_MODEL}")
    console.print(f"  Config: {MM_CLAUDE_CONFIG}")

    if _has_docker() and not no_docker:
        home = str(Path.home())
        volumes = [f"{home}/.mm-claude:/root/.mm-claude"]
        _docker_run(DOCKER_IMAGES["claude"], docker_env, docker_args, volumes=volumes)
    else:
        binary = _require_binary("claude", "npm install -g @anthropic-ai/claude-code")

        env = os.environ.copy()
        env.update(docker_env)
        env["CLAUDE_CONFIG_DIR"] = MM_CLAUDE_CONFIG
        # Remove auth token if set — conflicts with API key
        env.pop("ANTHROPIC_AUTH_TOKEN", None)

        args = [binary, "--model", DEFAULT_MODEL] + list(extra_args)
        console.print()
        os.execvpe(binary, args, env)


@launch.command()
@click.option("--no-docker", is_flag=True, help="Skip Docker, require local binary.")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def aider(no_docker: bool, extra_args: tuple):
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

    if _has_docker() and not no_docker:
        _docker_run(DOCKER_IMAGES["aider"], docker_env, docker_args,
                    run_as_host_user=True)
    else:
        binary = _require_binary("aider", "pip install aider-chat")
        _write_aider_config(key)

        env = os.environ.copy()
        env.update(docker_env)

        args = [binary, "--model", f"openai/{DEFAULT_MODEL}"] + list(extra_args)
        console.print()
        os.execvpe(binary, args, env)


@launch.command()
@click.option("--no-docker", is_flag=True, help="Skip Docker, require local binary.")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def codex(no_docker: bool, extra_args: tuple):
    """Launch Codex CLI with MiniMax-M2.5.

    Uses Docker if available, otherwise local install.
    """
    key = _require_key()

    console.print(f"[bold]Launching Codex[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_V1}")
    console.print(f"  Model: {DEFAULT_MODEL}")

    docker_env = {
        "OPENAI_BASE_URL": PUBLIC_API_V1,
        "OPENAI_API_KEY": key,
    }
    docker_args = ("--model", DEFAULT_MODEL) + extra_args

    if _has_docker() and not no_docker:
        _write_codex_config(key)
        home = str(Path.home())
        volumes = [f"{home}/.codex:/root/.codex"]
        _docker_run(DOCKER_IMAGES["codex"], docker_env, docker_args, volumes=volumes)
    else:
        binary = _require_binary("codex", "npm install -g @openai/codex")
        _write_codex_config(key)

        env = os.environ.copy()
        env.update(docker_env)

        args = [binary, "--model", DEFAULT_MODEL] + list(extra_args)
        console.print()
        os.execvpe(binary, args, env)


@launch.command()
@click.option("--no-docker", is_flag=True, help="Skip Docker, require local binary.")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def opencode(no_docker: bool, extra_args: tuple):
    """Launch OpenCode with MiniMax-M2.5.

    Uses Docker (ghcr.io/anomalyco/opencode) if available, otherwise local install.
    """
    key = _require_key()

    console.print(f"[bold]Launching OpenCode[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_V1}")

    docker_env = {
        "OPENAI_API_KEY": key,
    }
    model_arg = f"minimax/{DEFAULT_MODEL}"

    if _has_docker() and not no_docker:
        # Write project-level opencode.json in cwd
        _write_opencode_config(key)
        _docker_run(DOCKER_IMAGES["opencode"], docker_env,
                    ("--model", model_arg) + extra_args)
    else:
        binary = _require_binary("opencode", "go install github.com/opencode-ai/opencode@latest")
        _write_opencode_config(key)

        env = os.environ.copy()
        env.update(docker_env)

        args = [binary, "--model", model_arg] + list(extra_args)
        console.print()
        os.execvpe(binary, args, env)


@launch.command()
@click.option("--no-docker", is_flag=True, help="Skip Docker, require local binary.")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def openclaw(no_docker: bool, extra_args: tuple):
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

    if _has_docker() and not no_docker:
        home = str(Path.home())
        volumes = [f"{home}/.openclaw:/root/.openclaw"]
        docker_args = extra_args if extra_args else ("agent",)
        _docker_run(DOCKER_IMAGES["openclaw"], oc_env, docker_args, volumes=volumes)
    else:
        binary = _require_binary("openclaw", "pip install openclaw-cli")

        env = os.environ.copy()
        env.update(oc_env)

        if extra_args:
            args = [binary] + list(extra_args)
        else:
            args = [binary, "agent"]
        console.print()
        os.execvpe(binary, args, env)


@launch.command()
@click.option("--no-docker", is_flag=True, help="Skip Docker, require local binary.")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def nori(no_docker: bool, extra_args: tuple):
    """Launch Nori TUI with MiniMax-M2.5.

    Uses Docker if available, otherwise local install.
    Nori wraps Claude Code. MiniMax API provides an Anthropic-compatible
    translation layer so Nori works seamlessly.
    """
    key = _require_key()

    # Copy skills into Claude Code config dir
    _ensure_claude_skills()

    docker_env = {
        "ANTHROPIC_BASE_URL": PUBLIC_API_BASE,
        "ANTHROPIC_API_KEY": key,
        "CLAUDE_MODEL": DEFAULT_MODEL,
        "CLAUDE_CONFIG_DIR": "/root/.mm-claude",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    }

    console.print(f"[bold]Launching Nori[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_BASE}")
    console.print(f"  Model: {DEFAULT_MODEL}")

    if _has_docker() and not no_docker:
        home = str(Path.home())
        volumes = [f"{home}/.mm-claude:/root/.mm-claude"]
        _docker_run(DOCKER_IMAGES["nori"], docker_env, extra_args, volumes=volumes)
    else:
        binary = _require_binary("nori", "npm install -g nori-ai-cli")
        _ensure_senior_swe()

        env = os.environ.copy()
        env.update(docker_env)
        env["CLAUDE_CONFIG_DIR"] = MM_CLAUDE_CONFIG
        # Remove auth token if set — conflicts with API key
        env.pop("ANTHROPIC_AUTH_TOKEN", None)

        args = [binary] + list(extra_args)
        console.print()
        os.execvpe(binary, args, env)


@launch.command()
@click.option("--no-docker", is_flag=True, help="Skip Docker, require local binary.")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def toad(no_docker: bool, extra_args: tuple):
    """Launch Toad TUI with MiniMax-M2.5 (via ACP).

    Uses Docker if available, otherwise local install.
    """
    _require_key()

    console.print(f"[bold]Launching Toad[/] with MiniMax-M2.5 (via ACP)...")

    if _has_docker() and not no_docker:
        # Toad needs mm for ACP — both are in the Docker image
        docker_env = {
            "MINIMAX_API_KEY": get_api_key(),
        }
        docker_args = ("acp", "mm acp", "-t", "MiniMax-M2.5") + extra_args
        _docker_run(DOCKER_IMAGES["toad"], docker_env, docker_args)
    else:
        binary = _require_binary("toad", "pip install batrachian-toad")

        mm_bin = shutil.which("mm") or shutil.which("minimax")
        if not mm_bin:
            console.print("[red]mm binary not found in PATH[/]")
            raise SystemExit(1)

        args = [binary, "acp", f"{mm_bin} acp", "-t", "MiniMax-M2.5"] + list(extra_args)
        console.print()
        os.execvp(binary, args)


@launch.command()
@click.option("--no-docker", is_flag=True, help="Skip Docker, require local binary.")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def kimi(no_docker: bool, extra_args: tuple):
    """Launch Kimi CLI with MiniMax-M2.5.

    Uses Docker if available, otherwise local install.
    """
    key = _require_key()

    # Write kimi config with MiniMax provider
    _write_kimi_config(key)

    console.print(f"[bold]Launching Kimi CLI[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_V1}")
    console.print(f"  Model: {DEFAULT_MODEL}")

    docker_env = {
        "OPENAI_BASE_URL": PUBLIC_API_V1,
        "OPENAI_API_KEY": key,
    }
    docker_args = ("--model", DEFAULT_MODEL) + extra_args

    if _has_docker() and not no_docker:
        home = str(Path.home())
        volumes = [f"{home}/.kimi:/root/.kimi"]
        _docker_run(DOCKER_IMAGES["kimi"], docker_env, docker_args, volumes=volumes)
    else:
        binary = _require_binary("kimi", "pip install kimi-cli")

        env = os.environ.copy()
        env.update(docker_env)

        args = [binary, "--model", DEFAULT_MODEL] + list(extra_args)
        console.print()
        os.execvpe(binary, args, env)
