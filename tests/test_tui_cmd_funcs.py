"""Tests for tui_cmd functions."""

import pytest


class TestTuiCmdFuncs:
    def test_tui_cmd_importable(self):
        """Test tui_cmd is importable."""
        from minimax_cli.commands import tui_cmd
        assert tui_cmd is not None

    def test_tui_importable(self):
        """Test tui is importable."""
        from minimax_cli.commands.tui_cmd import tui
        assert tui is not None

    def test_find_repo_dir_importable(self):
        """Test _find_repo_dir is importable."""
        from minimax_cli.commands.tui_cmd import _find_repo_dir
        assert callable(_find_repo_dir)
