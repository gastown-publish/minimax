"""Tests for api module functions."""

import pytest
from unittest.mock import patch, MagicMock


class TestAPI:
    def test_base_url_construction(self):
        """Test _base_url builds correct URL."""
        from minimax_cli.api import _base_url
        url = _base_url("test-key")
        assert "api.minimax.villamarket.ai" in url
        assert url.startswith("https://")

    def test_headers_construction(self):
        """Test _headers builds correct headers."""
        from minimax_cli.api import _headers
        headers = _headers("test-key")
        assert "Authorization" in headers

    def test_check_health_importable(self):
        """Test check_health is importable."""
        from minimax_cli.api import check_health
        assert callable(check_health)

    def test_list_models_importable(self):
        """Test list_models is importable."""
        from minimax_cli.api import list_models
        assert callable(list_models)

    def test_verify_key_importable(self):
        """Test verify_key is importable."""
        from minimax_cli.api import verify_key
        assert callable(verify_key)
