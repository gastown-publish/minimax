"""Tests for minimax_cli.config module."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestConfig:
    """Tests for config functions."""

    @patch("minimax_cli.config.CONFIG_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("minimax_cli.config.CONFIG_FILE", new_callable=lambda: Path(tempfile.mktemp(suffix=".json")))
    def test_save_and_get_api_key(self, mock_config_file, mock_config_dir):
        """Test saving and retrieving API key."""
        from minimax_cli.config import save_api_key, get_api_key
        
        # Save key
        save_api_key("test-key-123")
        
        # Retrieve key
        key = get_api_key()
        
        assert key == "test-key-123"

    @patch("minimax_cli.config.CONFIG_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("minimax_cli.config.CONFIG_FILE", new_callable=lambda: Path(tempfile.mktemp(suffix=".json")))
    def test_delete_api_key(self, mock_config_file, mock_config_dir):
        """Test deleting API key."""
        from minimax_cli.config import save_api_key, get_api_key, delete_api_key
        
        # Save key first
        save_api_key("test-key-123")
        assert get_api_key() == "test-key-123"
        
        # Delete key
        delete_api_key()
        
        # Verify deleted
        assert get_api_key() is None

    @patch("minimax_cli.config.CONFIG_FILE", new_callable=lambda: Path("/nonexistent/file.json"))
    def test_get_api_key_missing_file(self, mock_config_file):
        """Test get_api_key returns None when file doesn't exist."""
        from minimax_cli.config import get_api_key
        
        result = get_api_key()
        
        assert result is None


class TestConfigPermissions:
    """Tests for config file permissions."""

    @patch("minimax_cli.config.CONFIG_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("minimax_cli.config.CONFIG_FILE", new_callable=lambda: Path(tempfile.mktemp(suffix=".json")))
    def test_config_file_permissions(self, mock_config_file, mock_config_dir):
        """Test config file is created with secure permissions (600)."""
        from minimax_cli.config import save_api_key
        import stat
        
        save_api_key("test-key-123")
        
        # Check permissions
        mode = mock_config_file.stat().st_mode
        assert mode & stat.S_IRWXG == 0  # No group permissions
        assert mode & stat.S_IRWXO == 0  # No other permissions
