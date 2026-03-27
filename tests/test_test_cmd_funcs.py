"""Tests for test_cmd functions."""

import pytest


class TestTestCmdFuncs:
    def test_test_cmd_importable(self):
        """Test test_cmd is importable."""
        from minimax_cli.commands import test_cmd
        assert test_cmd is not None

    def test_test_importable(self):
        """Test test is importable."""
        from minimax_cli.commands.test_cmd import test
        assert test is not None
