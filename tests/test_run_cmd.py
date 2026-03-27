"""Tests for minimax_cli.commands.run module."""

import pytest


class TestrunCmd:
    """Tests for run command."""

    def test_command_exists(self):
        """Test run command is registered."""
        from minimax_cli.commands.run import run
        assert run is not None
