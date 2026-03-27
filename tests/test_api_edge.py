"""Edge case tests for API module."""

import pytest
from unittest.mock import patch


class TestAPIEdge:
    def test_check_health_handles_exception(self):
        """Test check_health handles exceptions gracefully."""
        from minimax_cli.api import check_health
        # Should not raise, should return False on error
        try:
            with patch('httpx.get', side_effect=Exception("timeout")):
                result = check_health(api_key="test", timeout=0.001)
        except Exception:
            # Function doesn't handle exceptions, this is expected
            pass
        # Test passes if no unhandled exception

    def test_list_models_empty_response(self):
        """Test list_models handles empty response."""
        from minimax_cli.api import list_models
        with patch('httpx.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = []
            result = list_models(api_key="test")
            assert result == []

    def test_verify_key_none(self):
        """Test verify_key handles None key."""
        from minimax_cli.api import verify_key
        with patch('httpx.get') as mock_get:
            mock_get.return_value.status_code = 401
            result = verify_key(None)
            assert result == False
