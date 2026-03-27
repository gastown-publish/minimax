"""Tests for setup command functions."""

import pytest


class TestSetupFuncs:
    def test_setup_command_importable(self):
        """Test setup command is importable."""
        from minimax_cli.commands import setup
        assert setup is not None
