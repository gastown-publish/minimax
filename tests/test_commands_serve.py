"""Tests for minimax_cli.commands.serve module."""

import pytest

class TestServe:
    def test_serve_command_exists(self):
        from minimax_cli.commands.serve import serve
        assert serve is not None

    def test_stop_command_exists(self):
        from minimax_cli.commands.serve import stop
        assert stop is not None

    def test_logs_command_exists(self):
        from minimax_cli.commands.serve import logs
        assert logs is not None

    def test_require_server_env(self):
        from minimax_cli.commands.serve import _require_server_env
        assert _require_server_env is not None
