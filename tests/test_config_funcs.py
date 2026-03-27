"""Tests for config module functions."""

import pytest


class TestConfig:
    def test_get_api_key_importable(self):
        """Test get_api_key is importable."""
        from minimax_cli.config import get_api_key
        assert callable(get_api_key)

    def test_save_api_key_importable(self):
        """Test save_api_key is importable."""
        from minimax_cli.config import save_api_key
        assert callable(save_api_key)

    def test_delete_api_key_importable(self):
        """Test delete_api_key is importable."""
        from minimax_cli.config import delete_api_key
        assert callable(delete_api_key)

    def test_load_keys_importable(self):
        """Test load_keys is importable."""
        from minimax_cli.config import load_keys
        assert callable(load_keys)
