from __future__ import annotations
"""CLI entry point — registers all subcommands."""

import click

from . import __version__


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__, prog_name="mm")
def cli():
    """mm — MiniMax-M2.5 AI agent for your terminal."""


@cli.group("completion", context_settings=CONTEXT_SETTINGS)
def completion():
    """Generate shell completion scripts.

    \b
      mm completion bash          Print bash completion script
      mm completion zsh           Print zsh completion script
      mm completion fish          Print fish completion script
      mm completion install       Auto-install completion for current shell
    """


def _print_completion(shell: str):
    """Print the completion script for the given shell."""
    from click.shell_completion import get_completion_class

    comp_cls = get_completion_class(shell)
    if comp_cls is None:
        raise click.ClickException(f"Unsupported shell: {shell}")

    comp = comp_cls(cli, {}, "mm", "_MM_COMPLETE")
    click.echo(comp.source())


@completion.command("bash")
def completion_bash():
    """Print bash completion script."""
    _print_completion("bash")


@completion.command("zsh")
def completion_zsh():
    """Print zsh completion script."""
    _print_completion("zsh")


@completion.command("fish")
def completion_fish():
    """Print fish completion script."""
    _print_completion("fish")


@completion.command("install")
def completion_install():
    """Auto-install shell completion for your current shell.

    Detects your shell from $SHELL and appends the completion
    eval line to your rc file (idempotent — skips if already present).
    """
    import os
    from pathlib import Path

    shell_path = os.environ.get("SHELL", "")
    shell_name = Path(shell_path).name if shell_path else ""

    rc_map = {
        "bash": Path.home() / ".bashrc",
        "zsh": Path.home() / ".zshrc",
        "fish": Path.home() / ".config" / "fish" / "config.fish",
    }

    if shell_name not in rc_map:
        raise click.ClickException(
            f"Unsupported shell: {shell_path or '(not set)'}. "
            f"Supported: bash, zsh, fish"
        )

    rc_file = rc_map[shell_name]
    marker = "# mm shell completion"

    if rc_file.exists() and marker in rc_file.read_text():
        click.echo(f"Completion already installed in {rc_file}")
        return

    if shell_name == "fish":
        line = f"mm completion fish | source  {marker}"
    else:
        line = f'eval "$(mm completion {shell_name})"  {marker}'

    rc_file.parent.mkdir(parents=True, exist_ok=True)
    with open(rc_file, "a") as f:
        f.write(f"\n{line}\n")

    click.echo(f"Completion installed in {rc_file}")
    click.echo(f"Restart your shell or run: source {rc_file}")


@cli.command("upgrade")
def upgrade():
    """Upgrade mm to the latest version by re-running the install script."""
    import json
    import subprocess
    import urllib.request

    repo = "gastown-publish/minimax"
    click.echo("Checking for updates...")

    try:
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
        data = json.loads(urllib.request.urlopen(req, timeout=15).read())
        tag = data.get("tag_name", "")
        latest = tag.lstrip("v")
    except Exception as e:
        click.echo(f"Failed to check for updates: {e}", err=True)
        raise SystemExit(1)

    if latest == __version__:
        click.echo(f"Already up to date (v{__version__}).")
        return

    click.echo(f"Upgrading mm {__version__} → {latest}...")

    # Re-run the install script — it handles venv, wheel download, and symlinking
    result = subprocess.run(
        ["sh", "-c", "curl -fsSL minimax.villamarket.ai/install | sh"],
        text=True,
    )

    if result.returncode == 0:
        click.echo(f"Upgraded to mm {latest}")
    else:
        click.echo("Upgrade failed. Try manually:", err=True)
        click.echo("  curl -fsSL minimax.villamarket.ai/install | sh", err=True)
        raise SystemExit(1)


# Import and register command groups
from .commands.run import run
from .commands.serve import serve, stop, logs
from .commands.ps import ps, list_models
from .commands.test_cmd import test
from .commands.tui_cmd import tui
from .commands.auth import auth
from .commands.setup import setup
from .commands.term import term
from .commands.acp_cmd import acp
from .commands.launch import launch
from .commands.loop import loop
from .commands.skills_cmd import skills
from .commands.http import http

cli.add_command(run)
cli.add_command(http)
cli.add_command(serve)
cli.add_command(stop)
cli.add_command(logs)
cli.add_command(ps)
cli.add_command(list_models)
cli.add_command(test)
cli.add_command(tui)
cli.add_command(auth)
cli.add_command(setup)
cli.add_command(term)
cli.add_command(acp)
cli.add_command(launch)
cli.add_command(loop)
cli.add_command(skills)
