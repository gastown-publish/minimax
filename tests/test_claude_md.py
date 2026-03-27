"""Tests for claude_md module."""

import pytest
from pathlib import Path


class TestClaudeMD:
    def test_claude_md_importable(self):
        """Test claude_md is importable."""
        from minimax_cli import claude_md
        assert claude_md is not None
