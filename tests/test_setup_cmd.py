"""Tests for minimax_cli.commands.setup module."""

import pytest


class TestsetupCmd:
    """Tests for setup command."""

    def test_command_exists(self):
        """Test setup command is registered."""
        from minimax_cli.commands.setup import setup
        assert setup is not None
