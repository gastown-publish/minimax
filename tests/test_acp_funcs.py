"""Tests for ACP module functions."""

import pytest


class TestACPFuncs:
    def test_main_importable(self):
        """Test main is importable from acp."""
        from minimax_cli.acp import main
        assert main is not None

    def test_minimax_agent_importable(self):
        """Test MiniMaxAgent is importable from acp."""
        from minimax_cli.acp import MiniMaxAgent
        assert MiniMaxAgent is not None

    def test_server_main_importable(self):
        """Test server.main is importable."""
        from minimax_cli.acp.server import main as server_main
        assert callable(server_main)
