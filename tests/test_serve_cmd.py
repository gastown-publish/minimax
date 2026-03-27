"""Tests for minimax_cli.commands.serve module."""

import pytest


class TestserveCmd:
    """Tests for serve command."""

    def test_command_exists(self):
        """Test serve command is registered."""
        from minimax_cli.commands.serve import serve
        assert serve is not None
