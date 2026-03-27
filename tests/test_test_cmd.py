"""Test test_cmd import."""

import pytest


def test_test_cmd_import():
    """Test test_cmd is importable."""
    from minimax_cli.commands import test_cmd
    assert test_cmd is not None
