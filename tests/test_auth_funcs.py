"""Tests for auth command functions."""

import pytest


class TestAuthFuncs:
    def test_auth_command_importable(self):
        """Test auth command is importable."""
        from minimax_cli.commands import auth
        assert auth is not None

    def test_login_importable(self):
        """Test login is importable."""
        from minimax_cli.commands.auth import login
        assert login is not None

    def test_status_importable(self):
        """Test status is importable."""
        from minimax_cli.commands.auth import status
        assert status is not None

    def test_logout_importable(self):
        """Test logout is importable."""
        from minimax_cli.commands.auth import logout
        assert logout is not None
