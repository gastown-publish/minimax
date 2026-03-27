"""Tests for ACP server functions."""

import pytest
from pathlib import Path


class TestACPServer:
    def test_is_safe_path_importable(self):
        """Test _is_safe_path is importable."""
        from minimax_cli.acp.server import _is_safe_path
        assert callable(_is_safe_path)

    def test_build_system_prompt_importable(self):
        """Test _build_system_prompt is importable."""
        from minimax_cli.acp.server import _build_system_prompt
        assert callable(_build_system_prompt)

    def test_execute_tool_importable(self):
        """Test _execute_tool is importable."""
        from minimax_cli.acp.server import _execute_tool
        assert callable(_execute_tool)

    def test_minimax_agent_importable(self):
        """Test MiniMaxAgent is importable."""
        from minimax_cli.acp.server import MiniMaxAgent
        assert MiniMaxAgent is not None
