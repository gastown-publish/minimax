"""Tests for minimax_cli.commands.serve module."""

import pytest


class TestServe:
    """Tests for serve command functions."""

    def test_serve_command_exists(self):
        """Test serve command is registered."""
        from minimax_cli.commands.serve import serve
        assert serve is not None

    def test_stop_command_exists(self):
        """Test stop command is registered."""
        from minimax_cli.commands.serve import stop
        assert stop is not None

    def test_logs_command_exists(self):
        """Test logs command is registered."""
        from minimax_cli.commands.serve import logs
        assert logs is not None


class TestServeFunctions:
    """Tests for serve module functions."""

    def test_require_server_env_function(self):
        """Test _require_server_env function exists."""
        from minimax_cli.commands.serve import _require_server_env
        assert _require_server_env is not None
