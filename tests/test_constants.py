"""Tests for constants module."""

import pytest


class TestConstants:
    def test_constants_importable(self):
        """Test main constants are importable."""
        from minimax_cli.constants import (
            REPO_DIR, SCRIPTS_DIR, CONFIG_DIR, 
            VLLM_BASE, LITELLM_BASE, DEFAULT_MODEL
        )
        assert REPO_DIR is not None
        assert SCRIPTS_DIR is not None
        assert DEFAULT_MODEL is not None
