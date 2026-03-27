"""Tests for claude_md module functions."""

import pytest
from pathlib import Path


class TestClaudeMDFuncs:
    def test_claude_md_module_exists(self):
        """Test claude_md module is importable."""
        from minimax_cli import claude_md
        assert claude_md is not None

    def test_claude_md_is_module(self):
        """Test claude_md is a module type."""
        from minimax_cli import claude_md
        import types
        assert isinstance(claude_md, types.ModuleType)
