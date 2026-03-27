"""Tests for minimax_cli.commands.__init__ module."""

import pytest


class TestCommandsInit:
    """Tests for commands init utilities."""

    def test_console_exists(self):
        """Test console is defined."""
        from minimax_cli.commands import console
        assert console is not None

    def test_ensure_api_key_callable(self):
        """Test ensure_api_key is callable."""
        from minimax_cli.commands import ensure_api_key
        assert callable(ensure_api_key)
