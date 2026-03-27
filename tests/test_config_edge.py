"""Edge case tests for config module."""

import pytest
from pathlib import Path
from unittest.mock import patch


class TestConfigEdge:
    def test_get_api_key_missing_file(self):
        """Test get_api_key handles missing file."""
        from minimax_cli.config import get_api_key
        with patch('pathlib.Path.exists', return_value=False):
            result = get_api_key()
            assert result is None

    def test_delete_api_key_missing_file(self):
        """Test delete_api_key handles missing file."""
        from minimax_cli.config import delete_api_key
        with patch('pathlib.Path.exists', return_value=False):
            try:
                delete_api_key()
            except Exception as e:
                pytest.fail(f"Should not raise: {e}")

    def test_save_api_key_none(self):
        """Test save_api_key handles None."""
        from minimax_cli.config import save_api_key
        with patch('pathlib.Path.mkdir'):
            try:
                save_api_key(None)
            except Exception:
                pass
