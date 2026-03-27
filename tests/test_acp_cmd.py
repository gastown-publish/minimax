"""Tests for minimax_cli.commands.acp_cmd module."""

import pytest


class TestACPCmd:
    """Tests for acp command."""

    def test_acp_command_exists(self):
        """Test acp command is registered."""
        from minimax_cli.commands.acp_cmd import acp
        assert acp is not None
