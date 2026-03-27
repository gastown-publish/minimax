"""Advanced tests for config module."""

import pytest


class TestConfigAdvanced:
    def test_ensure_dir_importable(self):
        """Test _ensure_dir is importable."""
        from minimax_cli.config import _ensure_dir
        assert callable(_ensure_dir)

    def test_read_json_importable(self):
        """Test _read_json is importable."""
        from minimax_cli.config import _read_json
        assert callable(_read_json)

    def test_write_json_importable(self):
        """Test _write_json is importable."""
        from minimax_cli.config import _write_json
        assert callable(_write_json)

    def test_delete_api_key_importable(self):
        """Test delete_api_key is importable."""
        from minimax_cli.config import delete_api_key
        assert callable(delete_api_key)
