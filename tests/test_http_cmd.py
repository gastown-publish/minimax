"""Tests for minimax_cli.commands.http module."""

import pytest


class TestHTTPCmd:
    """Tests for http command."""

    def test_http_command_exists(self):
        """Test http command is registered."""
        from minimax_cli.commands.http import http
        assert http is not None
