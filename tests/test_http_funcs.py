"""Tests for http command functions."""

import pytest


class TestHTTPFuncs:
    def test_http_command_importable(self):
        """Test http command is importable."""
        from minimax_cli.commands import http
        assert http is not None

    def test_get_health_data_importable(self):
        """Test _get_health_data is importable."""
        from minimax_cli.commands.http import _get_health_data
        assert callable(_get_health_data)
