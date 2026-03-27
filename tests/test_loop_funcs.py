"""Tests for loop command functions."""

import pytest


class TestLoopFuncs:
    def test_loop_command_importable(self):
        """Test loop command is importable."""
        from minimax_cli.commands import loop
        assert loop is not None

    def test_git_context_importable(self):
        """Test _git_context is importable."""
        from minimax_cli.commands.loop import _git_context
        assert callable(_git_context)

    def test_load_state_importable(self):
        """Test _load_state is importable."""
        from minimax_cli.commands.loop import _load_state
        assert callable(_load_state)

    def test_save_state_importable(self):
        """Test _save_state is importable."""
        from minimax_cli.commands.loop import _save_state
        assert callable(_save_state)
