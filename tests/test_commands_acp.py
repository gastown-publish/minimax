"""Tests for minimax_cli.commands.acp_cmd module."""

import pytest

class TestACP:
    def test_acp_command_exists(self):
        from minimax_cli.commands.acp_cmd import acp
        assert acp is not None
