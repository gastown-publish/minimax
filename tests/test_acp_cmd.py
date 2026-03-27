"""Test acp_cmd import."""

import pytest


def test_acp_cmd_import():
    """Test acp_cmd is importable."""
    from minimax_cli.commands import acp_cmd
    assert acp_cmd is not None
