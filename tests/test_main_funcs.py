"""Tests for main.py functions."""

import pytest


class TestMainFuncs:
    def test_cli_importable(self):
        """Test cli is importable."""
        from minimax_cli.main import cli
        assert cli is not None

    def test_completion_importable(self):
        """Test completion is importable."""
        from minimax_cli.main import completion
        assert completion is not None

    def test_print_completion_importable(self):
        """Test _print_completion is importable."""
        from minimax_cli.main import _print_completion
        assert callable(_print_completion)

    def test_completion_bash_importable(self):
        """Test completion_bash is importable."""
        from minimax_cli.main import completion_bash
        assert completion_bash is not None
