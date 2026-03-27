"""Tests for serve command functions."""

import pytest


class TestServeFuncs:
    def test_serve_command_importable(self):
        """Test serve command is importable."""
        from minimax_cli.commands import serve
        assert serve is not None

    def test_require_server_env_importable(self):
        """Test _require_server_env is importable."""
        from minimax_cli.commands.serve import _require_server_env
        assert callable(_require_server_env)

    def test_stop_importable(self):
        """Test stop is importable."""
        from minimax_cli.commands.serve import stop
        assert stop is not None

    def test_logs_importable(self):
        """Test logs is importable."""
        from minimax_cli.commands.serve import logs
        assert logs is not None
