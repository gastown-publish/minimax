"""Tests for minimax_cli.commands.tui_cmd module."""

import pytest


class TestTuiCmd:
    """Tests for tui command."""

    def test_tui_command_exists(self):
        """Test tui command is registered."""
        from minimax_cli.commands.tui_cmd import tui
        assert tui is not None
