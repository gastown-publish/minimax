"""CLI entry point — registers all subcommands."""

import click

from . import __version__


@click.group()
@click.version_option(__version__, prog_name="mm")
def cli():
    """mm — MiniMax-M2.5 AI agent for your terminal."""


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
from .commands.loop import loop
from .commands.skills_cmd import skills

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
cli.add_command(term)
cli.add_command(acp)
cli.add_command(loop)
cli.add_command(skills)
