"""Tests for minimax_cli.commands.run module."""

import pytest

class TestRun:
    def test_run_command_exists(self):
        from minimax_cli.commands.run import run
        assert run is not None
