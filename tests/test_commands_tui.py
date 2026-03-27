"""Tests for minimax_cli.commands.tui_cmd module."""

import pytest

class TestTUI:
    def test_tui_command_exists(self):
        from minimax_cli.commands.tui_cmd import tui
        assert tui is not None
