"""Tests for edge cases."""

import pytest


class TestEdgeCases:
    def test_version_format(self):
        """Test version is properly formatted."""
        from minimax_cli import __version__
        # Version should be string like "x.y.z" or "x.y.z-dev"
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_api_key_none_handling(self):
        """Test API functions handle None key."""
        from minimax_cli.api import _base_url, _headers
        url = _base_url(None)
        assert "https://" in url
        headers = _headers(None)
        assert isinstance(headers, dict)
