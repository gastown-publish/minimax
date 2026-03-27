"""Tests for acp_cmd functions."""

import pytest


class TestAcpCmdFuncs:
    def test_acp_cmd_importable(self):
        """Test acp_cmd is importable."""
        from minimax_cli.commands import acp_cmd
        assert acp_cmd is not None

    def test_acp_importable(self):
        """Test acp is importable."""
        from minimax_cli.commands.acp_cmd import acp
        assert acp is not None
