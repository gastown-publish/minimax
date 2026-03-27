"""Tests for run command functions."""

import pytest


class TestRunFuncs:
    def test_run_command_importable(self):
        """Test run command is importable."""
        from minimax_cli.commands import run
        assert run is not None
