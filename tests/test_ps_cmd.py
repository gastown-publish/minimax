"""Tests for minimax_cli.commands.ps module."""

import pytest


class TestpsCmd:
    """Tests for ps command."""

    def test_command_exists(self):
        """Test ps command is registered."""
        from minimax_cli.commands.ps import ps
        assert ps is not None
