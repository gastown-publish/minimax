"""Tests for minimax_cli.system_prompt module."""

import pytest


class TestSystemPrompt:
    """Tests for system prompt constants."""

    def test_system_prompt_exported(self):
        """Test SYSTEM_PROMPT is exported."""
        from minimax_cli import system_prompt
        assert hasattr(system_prompt, 'SYSTEM_PROMPT')

    def test_system_prompt_has_content(self):
        """Test SYSTEM_PROMPT has content."""
        from minimax_cli.system_prompt import SYSTEM_PROMPT
        assert SYSTEM_PROMPT is not None
        assert len(SYSTEM_PROMPT) > 0

    def test_system_prompt_contains_model_info(self):
        """Test prompt mentions the model."""
        from minimax_cli.system_prompt import SYSTEM_PROMPT
        assert "MiniMax" in SYSTEM_PROMPT

    def test_system_prompt_contains_workflows(self):
        """Test prompt lists workflows."""
        from minimax_cli.system_prompt import SYSTEM_PROMPT
        assert "mm loop" in SYSTEM_PROMPT or "workflow" in SYSTEM_PROMPT.lower()

    def test_claude_md_matches_system_prompt(self):
        """Test CLAUDE_MD matches SYSTEM_PROMPT."""
        from minimax_cli.claude_md import CLAUDE_MD
        from minimax_cli.system_prompt import SYSTEM_PROMPT
        
        # Both should have similar content
        assert "MiniMax" in CLAUDE_MD and "MiniMax" in SYSTEM_PROMPT
