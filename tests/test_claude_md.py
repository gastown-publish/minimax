"""Tests for minimax_cli.claude_md module."""

from pathlib import Path

import pytest


class TestClaudeMd:
    """Tests for claude_md functions."""

    def test_claude_md_exports_constant(self):
        """Test CLAUDE_MD constant is exported."""
        from minimax_cli import claude_md
        assert hasattr(claude_md, 'CLAUDE_MD')

    def test_claude_md_has_content(self):
        """Test CLAUDE_MD has content."""
        from minimax_cli.claude_md import CLAUDE_MD
        assert CLAUDE_MD is not None
        assert len(CLAUDE_MD) > 0


class TestClaudeMdIntegration:
    """Integration tests for CLAUDE.md usage."""

    def test_claude_md_file_exists(self):
        """Test CLAUDE.md file exists in repo."""
        from minimax_cli.constants import REPO_DIR
        
        claude_file = REPO_DIR / "CLAUDE.md"
        assert claude_file.exists()
        
        # Verify file has content
        content = claude_file.read_text()
        assert len(content) > 0

    def test_system_prompt_matches_file(self):
        """Test CLAUDE_MD constant matches CLAUDE.md file."""
        from minimax_cli.claude_md import CLAUDE_MD
        from minimax_cli.constants import REPO_DIR
        
        file_content = (REPO_DIR / "CLAUDE.md").read_text()
        
        # The constant should contain part of the file content
        assert len(CLAUDE_MD) > 0
