"""CLI entry point — registers all subcommands."""

import click

from . import __version__


@click.group()
@click.version_option(__version__, prog_name="minimax")
def cli():
    """MiniMax-M2.5 — Ollama-style CLI for self-hosted inference."""


# Import and register command groups
from .commands.run import run
from .commands.serve import serve, stop, logs
from .commands.ps import ps, list_models
from .commands.test_cmd import test
from .commands.tui_cmd import tui
from .commands.auth import auth
from .commands.setup import setup

cli.add_command(run)
cli.add_command(serve)
cli.add_command(stop)
cli.add_command(logs)
cli.add_command(ps)
cli.add_command(list_models)
cli.add_command(test)
cli.add_command(tui)
cli.add_command(auth)
cli.add_command(setup)
