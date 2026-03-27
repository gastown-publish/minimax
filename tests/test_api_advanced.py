"""Advanced tests for API module functions."""

import pytest
from unittest.mock import patch, MagicMock


class TestAPIAdvanced:
    def test_check_health_with_mock(self):
        """Test check_health returns True on success."""
        from minimax_cli.api import check_health
        with patch('httpx.get') as mock_get:
            mock_get.return_value.status_code = 200
            result = check_health(api_key="test-key", timeout=5)
            assert result == True

    def test_list_models_with_mock(self):
        """Test list_models returns list on success."""
        from minimax_cli.api import list_models
        with patch('httpx.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = [{"id": "model1"}]
            result = list_models(api_key="test-key", timeout=5)
            assert isinstance(result, list)

    def test_base_url_with_none(self):
        """Test _base_url handles None api_key."""
        from minimax_cli.api import _base_url
        url = _base_url(None)
        assert "api.minimax.villamarket.ai" in url

    def test_headers_with_key(self):
        """Test _headers returns auth with api_key."""
        from minimax_cli.api import _headers
        headers = _headers("test-key")
        assert isinstance(headers, dict)
        assert "Authorization" in headers
        assert "Bearer" in headers["Authorization"]
