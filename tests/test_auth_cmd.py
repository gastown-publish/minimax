"""Tests for minimax_cli.commands.auth module."""

import pytest


class TestAuthCmd:
    """Tests for auth command."""

    def test_auth_command_exists(self):
        """Test auth command is registered."""
        from minimax_cli.commands.auth import auth
        assert auth is not None
