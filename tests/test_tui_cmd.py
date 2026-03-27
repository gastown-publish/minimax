"""Test tui_cmd import."""

import pytest


def test_tui_cmd_import():
    """Test tui_cmd is importable."""
    from minimax_cli.commands import tui_cmd
    assert tui_cmd is not None
