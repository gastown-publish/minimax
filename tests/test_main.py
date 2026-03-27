"""Tests for minimax_cli.main module (CLI entry point)."""

from click.testing import CliRunner

import pytest


class TestCLI:
    """Tests for CLI entry point."""

    def test_cli_help(self):
        """Test --help shows usage."""
        from minimax_cli.main import cli
        
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        
        assert result.exit_code == 0
        assert "mm — MiniMax-M2.5" in result.output

    def test_cli_version(self):
        """Test --version shows version."""
        from minimax_cli.main import cli
        from minimax_cli import __version__
        
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_completion_bash(self):
        """Test bash completion command."""
        from minimax_cli.main import completion_bash
        
        runner = CliRunner()
        result = runner.invoke(completion_bash)
        
        assert result.exit_code == 0

    def test_completion_zsh(self):
        """Test zsh completion command."""
        from minimax_cli.main import completion_zsh
        
        runner = CliRunner()
        result = runner.invoke(completion_zsh)
        
        assert result.exit_code == 0

    def test_completion_fish(self):
        """Test fish completion command."""
        from minimax_cli.main import completion_fish
        
        runner = CliRunner()
        result = runner.invoke(completion_fish)
        
        assert result.exit_code == 0

    def test_all_commands_registered(self):
        """Test all expected commands are registered."""
        from minimax_cli.main import cli
        
        command_names = [cmd.name for cmd in cli.commands.values()]
        
        expected = ["run", "http", "serve", "stop", "logs", "ps", "list", 
                   "test", "tui", "auth", "setup", "term", "acp", "launch", "loop", "skills"]
        for cmd in expected:
            assert cmd in command_names, f"Command {cmd} not registered"
