"""Tests for minimax_cli.commands.auth module."""

import pytest

class TestAuth:
    def test_auth_group_exists(self):
        from minimax_cli.commands.auth import auth
        assert auth is not None

    def test_login_command_exists(self):
        from minimax_cli.commands.auth import login
        assert login is not None

    def test_logout_command_exists(self):
        from minimax_cli.commands.auth import logout
        assert logout is not None
