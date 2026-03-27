"""Tests for minimax_cli.constants module."""

import os
from pathlib import Path

import pytest


class TestConstants:
    """Tests for constants values."""

    def test_api_urls_defined(self):
        """Test all API URLs are defined."""
        from minimax_cli.constants import (
            VLLM_BASE, LITELLM_BASE, PUBLIC_API_BASE, PUBLIC_API_V1
        )
        
        assert VLLM_BASE == "http://localhost:8080"
        assert LITELLM_BASE == "http://localhost:4000"
        assert PUBLIC_API_BASE == "https://api.minimax.villamarket.ai"
        assert PUBLIC_API_V1 == "https://api.minimax.villamarket.ai/v1"

    def test_model_ids_defined(self):
        """Test model IDs are defined."""
        from minimax_cli.constants import MODEL_IDS, DEFAULT_MODEL
        
        assert "minimax-m2.5" in MODEL_IDS
        assert "MiniMaxAI/MiniMax-M2.5" in MODEL_IDS
        assert DEFAULT_MODEL == "minimax-m2.5"

    def test_context_windows_defined(self):
        """Test context window constants are defined."""
        from minimax_cli.constants import CONTEXT_WINDOW, OUTPUT_WINDOW, FULL_CONTEXT
        
        assert CONTEXT_WINDOW == 128_000
        assert OUTPUT_WINDOW == 16_384
        assert FULL_CONTEXT == 131_072

    def test_paths_configured(self):
        """Test path constants are configured."""
        from minimax_cli.constants import (
            CONFIG_DIR, CONFIG_FILE, KEYS_FILE, VLLM_LOG, LITELLM_LOG
        )
        
        # These should be Path objects
        assert isinstance(CONFIG_DIR, Path)
        assert isinstance(CONFIG_FILE, Path)
        assert isinstance(KEYS_FILE, Path)

    def test_ses_configured(self):
        """Test SES configuration is defined."""
        from minimax_cli.constants import SES_SENDER, SES_REGION
        
        assert SES_SENDER == "noreply@villamarket.ai"
        assert SES_REGION == "us-east-1"
