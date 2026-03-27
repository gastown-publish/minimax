"""Tests for acp command module."""

import pytest


class TestACPCommand:
    def test_acp_import(self):
        from minimax_cli.commands.acp_cmd import acp
        assert acp is not None
