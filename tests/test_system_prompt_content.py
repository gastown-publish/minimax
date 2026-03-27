"""Tests for system_prompt module."""

import pytest


class TestSystemPrompt:
    def test_system_prompt_module_importable(self):
        """Test system_prompt module is importable."""
        from minimax_cli import system_prompt
        assert system_prompt is not None

    def test_system_prompt_constant_importable(self):
        """Test SYSTEM_PROMPT constant is importable."""
        from minimax_cli.system_prompt import SYSTEM_PROMPT
        assert isinstance(SYSTEM_PROMPT, str)
        assert len(SYSTEM_PROMPT) > 0
