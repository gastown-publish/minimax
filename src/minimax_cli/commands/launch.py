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


__all__ = ["_check_api", "_require_key", "_has_docker", "_docker_run", "_find_binary", "_require_binary", "_ensure_senior_swe", "_write_codex_config", "_write_opencode_config", "_write_aider_config", "_write_kimi_config", "_ensure_claude_skills", "launch", "claude", "aider", "codex", "opencode", "openclaw", "nori", "toad", "kimi", "_write_gasclaw_compose", "gasclaw"]
def _check_api(key: str) -> bool:
    """Quick API connectivity check — GET /v1/models with the key."""
    import urllib.request
    import urllib.error

    try:
        req = urllib.request.Request(
            f"{PUBLIC_API_V1}/models",
            headers={"Authorization": f"Bearer {key}"},
        )
        resp = urllib.request.urlopen(req, timeout=5)  # nosec B310
        if resp.status == 200:
            console.print("  [green]API: connected[/]")
            return True
    except urllib.error.HTTPError as e:
        if e.code == 401:
            console.print("  [red]API: invalid key (401)[/]")
        else:
            console.print(f"  [yellow]API: HTTP {e.code}[/]")
        return False
    except Exception:
        console.print("  [yellow]API: unreachable (continuing anyway)[/]")
    return False

# Docker Hub namespace (public by default, no auth needed to pull)
DOCKER_HUB = "thanakijwanavit"

# Docker images for tools that support them
DOCKER_IMAGES = {
    "aider": "paulgauthier/aider",
    "openclaw": "ghcr.io/openclaw/openclaw:latest",
    "claude": f"{DOCKER_HUB}/mm-claude:latest",
    "opencode": f"{DOCKER_HUB}/mm-opencode:latest",
    "codex": f"{DOCKER_HUB}/mm-codex:latest",
    "nori": f"{DOCKER_HUB}/mm-nori:latest",
    "kimi": f"{DOCKER_HUB}/mm-kimi:latest",
    "toad": f"{DOCKER_HUB}/mm-toad:latest",
    "minimax": f"{DOCKER_HUB}/minimax:latest",
    "gasclaw": f"{DOCKER_HUB}/gasclaw:latest",
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
    from ..system_prompt import SYSTEM_PROMPT

    config_dir = Path.home() / ".codex"
    config_file = config_dir / "config.yaml"
    instructions_file = config_dir / "instructions.md"
    config_dir.mkdir(parents=True, exist_ok=True)
    instructions_file.write_text(SYSTEM_PROMPT)
    config_file.write_text(
        f"provider: openai\n"
        f"model: {DEFAULT_MODEL}\n"
        f"base_url: {PUBLIC_API_V1}\n"
        f"api_key: {key}\n"
    )


def _write_opencode_config(cwd: str | None = None):
    """Write OpenCode project config (opencode.json) in cwd.

    Uses the built-in openai provider with OPENAI_BASE_URL env var
    to work around custom provider options bug (sst/opencode#5674).
    API key is passed via OPENAI_API_KEY env var.
    """
    from ..system_prompt import SYSTEM_PROMPT

    target = Path(cwd or os.getcwd()) / "opencode.json"
    target.write_text(json.dumps({
        "$schema": "https://opencode.ai/config.json",
        "model": f"openai/{DEFAULT_MODEL}",
        "instructions": SYSTEM_PROMPT,
        "provider": {
            "openai": {
                "models": {
                    DEFAULT_MODEL: {
                        "name": "MiniMax-M2.5",
                        "limit": {"context": 128000, "output": 16384},
                    }
                },
            }
        },
    }, indent=2) + "\n")


def _write_aider_config(key: str):
    """Write Aider config file with system prompt."""
    from ..system_prompt import SYSTEM_PROMPT

    config_file = Path.home() / ".aider.conf.yml"
    # Write system prompt to a file that aider can read
    prompt_file = Path.home() / ".aider.system-prompt.md"
    prompt_file.write_text(SYSTEM_PROMPT)
    config_file.write_text(
        f"openai-api-base: {PUBLIC_API_V1}\n"
        f"openai-api-key: {key}\n"
        f"model: openai/{DEFAULT_MODEL}\n"
        f"read: [{prompt_file}]\n"
    )


def _write_kimi_config(key: str):
    """Write Kimi CLI config with MiniMax provider and system prompt."""
    from ..system_prompt import SYSTEM_PROMPT

    config_dir = Path.home() / ".kimi"
    config_file = config_dir / "config.toml"
    config_dir.mkdir(parents=True, exist_ok=True)

    # Escape the system prompt for TOML multiline string
    escaped = SYSTEM_PROMPT.replace('\\', '\\\\').replace("'''", "\\'\\'\\'")

    config = (
        f'default_model = "{DEFAULT_MODEL}"\n'
        f'default_thinking = false\n'
        f"system_prompt = '''\n{escaped}'''\n"
        f'\n'
        f'[models."{DEFAULT_MODEL}"]\n'
        f'provider = "minimax"\n'
        f'model = "{DEFAULT_MODEL}"\n'
        f'max_context_size = 131072\n'
        f'\n'
        f'[providers."minimax"]\n'
        f'type = "openai_legacy"\n'
        f'base_url = "{PUBLIC_API_V1}"\n'
        f'api_key = "{key}"\n'
    )
    config_file.write_text(config)


def _ensure_claude_skills():
    """Copy bundled skills + Nori skills + CLAUDE.md into Claude Code config.

    Claude Code reads skills from ~/.claude/skills/ (global)
    and .claude/skills/ (project). We write to the global dir.
    Also writes CLAUDE.md to the mm-claude config dir so the agent
    has context about itself, available skills, and ecosystem.
    """
    from ..skills import SKILLS_DIR
    from ..system_prompt import CLAUDE_SYSTEM_PROMPT as CLAUDE_MD

    # Claude Code always uses ~/.claude/skills/ regardless of CLAUDE_CONFIG_DIR
    target_dir = Path.home() / ".claude" / "skills"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Also install skills into the mm-claude config dir
    mm_skills_dir = Path(MM_CLAUDE_CONFIG) / "skills"
    mm_skills_dir.mkdir(parents=True, exist_ok=True)

    # Copy bundled skills to both locations
    for skill_file in SKILLS_DIR.glob("*.md"):
        for dest_dir in (target_dir, mm_skills_dir):
            dest = dest_dir / skill_file.name
            if not dest.exists() or dest.read_text() != skill_file.read_text():
                dest.write_text(skill_file.read_text())

    # Copy Nori skills if available
    nori_skills_dir = Path.home() / ".nori" / "profiles" / "senior-swe" / "skills"
    if nori_skills_dir.is_dir():
        for dest_dir in (target_dir, mm_skills_dir):
            nori_target = dest_dir / "nori"
            nori_target.mkdir(parents=True, exist_ok=True)
            for skill_dir in nori_skills_dir.iterdir():
                if skill_dir.is_dir():
                    for md_name in ("SKILL.md", "prompt.md"):
                        md_file = skill_dir / md_name
                        if md_file.exists():
                            dest = nori_target / f"{skill_dir.name}.md"
                            content = md_file.read_text()
                            if not dest.exists() or dest.read_text() != content:
                                dest.write_text(content)
                            break

    # Write CLAUDE.md to mm-claude config dir (agent system context)
    claude_md_path = Path(MM_CLAUDE_CONFIG) / "CLAUDE.md"
    if not claude_md_path.exists() or claude_md_path.read_text() != CLAUDE_MD:
        claude_md_path.write_text(CLAUDE_MD)


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
    from ..system_prompt import CLAUDE_SYSTEM_PROMPT

    docker_args = (
        "--model", DEFAULT_MODEL,
        "--append-system-prompt", CLAUDE_SYSTEM_PROMPT,
    ) + extra_args

    console.print(f"[bold]Launching Claude Code[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_BASE}")
    console.print(f"  Model: {DEFAULT_MODEL}")
    console.print(f"  Config: {MM_CLAUDE_CONFIG}")
    _check_api(key)

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

        args = [binary, "--model", DEFAULT_MODEL,
                "--append-system-prompt", CLAUDE_SYSTEM_PROMPT] + list(extra_args)
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
    _check_api(key)

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
    _check_api(key)

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

    Uses Docker if available, otherwise local install.
    """
    key = _require_key()

    console.print(f"[bold]Launching OpenCode[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_V1}")
    _check_api(key)

    docker_env = {
        "OPENAI_API_KEY": key,
        "OPENAI_BASE_URL": PUBLIC_API_V1,
    }

    if _has_docker() and not no_docker:
        # Write project-level opencode.json in cwd — model set there
        _write_opencode_config()
        _docker_run(DOCKER_IMAGES["opencode"], docker_env, extra_args)
    else:
        binary = _require_binary("opencode", "curl -fsSL https://opencode.ai/install | bash")
        _write_opencode_config()

        env = os.environ.copy()
        env.update(docker_env)

        args = [binary] + list(extra_args)
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
    _check_api(key)

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
    _check_api(key)

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
    _check_api(key)

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


GASCLAW_COMPOSE = """\
services:
  gasclaw:
    image: {image}
    container_name: gasclaw
    ports:
      - "{gateway_port}:18789"
    volumes:
      - {project_dir}:/project
      - gasclaw-openclaw:/root/.openclaw
      - gasclaw-dolt:/root/.dolt
      - gasclaw-state:/root/.gasclaw
      - gasclaw-claude:/root/.claude-config
      - gasclaw-workspace:/workspace
    environment:
      - GASTOWN_KIMI_KEYS={api_key}
      - OPENCLAW_KIMI_KEY={api_key}
      - TELEGRAM_BOT_TOKEN={telegram_bot_token}
      - TELEGRAM_OWNER_ID={telegram_owner_id}
      - ANTHROPIC_BASE_URL={api_base}
      - GT_AGENT_COUNT={agent_count}
    restart: unless-stopped

volumes:
  gasclaw-openclaw:
  gasclaw-dolt:
  gasclaw-state:
  gasclaw-claude:
  gasclaw-workspace:
"""


def _write_gasclaw_compose(
    key: str,
    *,
    telegram_bot_token: str,
    telegram_owner_id: str,
    project_dir: str | None = None,
    gateway_port: int = 18789,
    agent_count: int = 6,
) -> Path:
    """Write docker-compose.gasclaw.yml for running Gasclaw with MiniMax."""
    compose_file = Path.home() / ".mm-gasclaw" / "docker-compose.yml"
    compose_file.parent.mkdir(parents=True, exist_ok=True)

    content = GASCLAW_COMPOSE.format(
        image=DOCKER_IMAGES.get("gasclaw", f"{DOCKER_HUB}/gasclaw:latest"),
        api_key=key,
        api_base=PUBLIC_API_BASE,
        telegram_bot_token=telegram_bot_token,
        telegram_owner_id=telegram_owner_id,
        project_dir=project_dir or os.getcwd(),
        gateway_port=gateway_port,
        agent_count=agent_count,
    )
    compose_file.write_text(content)
    return compose_file


@launch.command()
@click.option("--telegram-bot-token", envvar="TELEGRAM_BOT_TOKEN",
              help="Telegram bot token (from @BotFather).")
@click.option("--telegram-owner-id", envvar="TELEGRAM_OWNER_ID",
              help="Telegram user ID (numeric).")
@click.option("--project", "-p", default=None,
              help="Project directory to mount (default: cwd).")
@click.option("--agents", default=6, show_default=True,
              help="Number of crew workers.")
@click.option("--port", default=18789, show_default=True,
              help="Gateway port.")
@click.option("--stop", "do_stop", is_flag=True, help="Stop running Gasclaw.")
@click.option("--logs", "do_logs", is_flag=True, help="Show Gasclaw logs.")
@click.option("--status", "do_status", is_flag=True, help="Show Gasclaw status.")
def gasclaw(telegram_bot_token, telegram_owner_id, project, agents, port,
            do_stop, do_logs, do_status):
    """Launch Gasclaw multi-agent orchestration with MiniMax-M2.5.

    Gasclaw runs Gastown (agent coordination) + OpenClaw (Telegram oversight)
    in a single Docker container, using MiniMax-M2.5 as the LLM backend.

    \b
    First run:
        mm launch gasclaw --telegram-bot-token TOKEN --telegram-owner-id ID

    \b
    Management:
        mm launch gasclaw --stop     Stop Gasclaw
        mm launch gasclaw --logs     View logs
        mm launch gasclaw --status   Show status
    """
    compose_dir = Path.home() / ".mm-gasclaw"
    compose_file = compose_dir / "docker-compose.yml"

    # Management subcommands (don't need API key)
    if do_stop:
        if not compose_file.exists():
            console.print("[red]Gasclaw not initialized.[/] Run: mm launch gasclaw")
            raise SystemExit(1)
        os.execvp("docker", ["docker", "compose", "-f", str(compose_file), "down"])

    if do_logs:
        if not compose_file.exists():
            console.print("[red]Gasclaw not initialized.[/]")
            raise SystemExit(1)
        os.execvp("docker", ["docker", "compose", "-f", str(compose_file), "logs", "-f"])

    if do_status:
        if not compose_file.exists():
            console.print("[red]Gasclaw not initialized.[/]")
            raise SystemExit(1)
        os.execvp("docker", ["docker", "compose", "-f", str(compose_file), "ps"])

    # Starting Gasclaw — need key and Telegram config
    key = _require_key()

    if not _has_docker():
        console.print("[red]Docker is required for Gasclaw.[/]")
        raise SystemExit(1)

    # Check for Telegram config
    if not telegram_bot_token:
        # Check if compose file exists (reuse existing config)
        if compose_file.exists():
            console.print("[bold]Starting Gasclaw[/] (using existing config)...")
            os.execvp("docker", [
                "docker", "compose", "-f", str(compose_file), "up", "-d",
            ])
        console.print("[red]Telegram bot token required.[/]")
        console.print("  mm launch gasclaw --telegram-bot-token TOKEN --telegram-owner-id ID")
        console.print("")
        console.print("Get a bot token from @BotFather on Telegram.")
        raise SystemExit(1)

    if not telegram_owner_id:
        console.print("[red]Telegram owner ID required.[/]")
        console.print("  Get your ID from @userinfobot on Telegram.")
        raise SystemExit(1)

    # Write compose file and start
    compose_path = _write_gasclaw_compose(
        key,
        telegram_bot_token=telegram_bot_token,
        telegram_owner_id=telegram_owner_id,
        project_dir=project,
        gateway_port=port,
        agent_count=agents,
    )

    console.print(f"[bold]Launching Gasclaw[/] with MiniMax-M2.5...")
    console.print(f"  API: {PUBLIC_API_BASE}")
    console.print(f"  Agents: {agents}")
    console.print(f"  Gateway: http://localhost:{port}")
    console.print(f"  Project: {project or os.getcwd()}")
    console.print(f"  Config: {compose_path}")
    console.print()

    os.execvp("docker", [
        "docker", "compose", "-f", str(compose_path), "up", "-d",
    ])
