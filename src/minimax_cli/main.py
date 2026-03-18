"""CLI entry point — registers all subcommands."""

import click

from . import __version__


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__, prog_name="mm")
def cli():
    """mm — MiniMax-M2.5 AI agent for your terminal."""


@cli.command("completion")
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish"]))
def completion(shell: str):
    """Generate shell completion script.

    Add to your shell profile:

    \b
      bash:  eval "$(mm completion bash)"
      zsh:   eval "$(mm completion zsh)"
      fish:  mm completion fish | source
    """
    from click.shell_completion import get_completion_class

    comp_cls = get_completion_class(shell)
    if comp_cls is None:
        raise click.ClickException(f"Unsupported shell: {shell}")

    comp = comp_cls(cli, {}, "mm", "_MM_COMPLETE")
    click.echo(comp.source())


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
cli.add_command(launch)
