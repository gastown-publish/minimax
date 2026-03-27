"""Tests for minimax_cli.api module."""

from unittest.mock import patch, MagicMock
import httpx
import sys


class TestCheckHealth:
    """Tests for check_health function."""

    @patch("minimax_cli.api.httpx.get")
    def test_health_endpoint_success(self, mock_get):
        """Test health check returns True when /health/liveliness responds 200."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        from minimax_cli.api import check_health
        result = check_health(api_key="test-key")

        assert result is True

    @patch("minimax_cli.api.httpx.get")
    def test_all_endpoints_fail(self, mock_get):
        """Test health check returns False when all endpoints fail."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        from minimax_cli.api import check_health
        result = check_health(api_key="test-key", timeout=1)

        assert result is False


class TestListModels:
    """Tests for list_models function."""

    @patch("minimax_cli.api.httpx.get")
    def test_list_models_success(self, mock_get):
        """Test list_models returns model data."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "model1"}]}
        mock_get.return_value = mock_response

        from minimax_cli.api import list_models
        result = list_models(api_key="test-key")

        assert len(result) == 1
        assert result[0]["id"] == "model1"

    @patch("minimax_cli.api.httpx.get")
    def test_list_models_empty(self, mock_get):
        """Test list_models returns empty list on error."""
        mock_get.side_effect = httpx.ConnectError("Connection failed")

        from minimax_cli.api import list_models
        result = list_models(api_key="test-key")

        assert result == []


class TestVerifyKey:
    """Tests for verify_key function."""

    @patch("minimax_cli.api.httpx.get")
    def test_verify_key_success(self, mock_get):
        """Test verify_key returns True on successful auth."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        from minimax_cli.api import verify_key
        result = verify_key("test-key-123")

        assert result is True

    @patch("minimax_cli.api.httpx.get")
    def test_verify_key_failure(self, mock_get):
        """Test verify_key returns False on auth failure."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        from minimax_cli.api import verify_key
        result = verify_key("invalid-key")

        assert result is False
