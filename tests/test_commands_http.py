"""Tests for minimax_cli.commands.http module."""

import pytest

class TestHTTP:
    def test_http_command_exists(self):
        from minimax_cli.commands.http import http
        assert http is not None
