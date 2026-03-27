"""Tests for tui command module."""

import pytest


class TestTUICommand:
    def test_tui_import(self):
        from minimax_cli.commands.tui_cmd import tui
        assert tui is not None
