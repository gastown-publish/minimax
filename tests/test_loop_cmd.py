"""Tests for minimax_cli.commands.loop module."""

import pytest


class TestloopCmd:
    """Tests for loop command."""

    def test_command_exists(self):
        """Test loop command is registered."""
        from minimax_cli.commands.loop import loop
        assert loop is not None
