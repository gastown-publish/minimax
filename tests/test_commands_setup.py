"""Tests for minimax_cli.commands.setup module."""

import pytest

class TestSetup:
    def test_setup_command_exists(self):
        from minimax_cli.commands.setup import setup
        assert setup is not None
