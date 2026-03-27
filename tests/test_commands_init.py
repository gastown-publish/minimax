"""Tests for commands __init__."""

import pytest


class TestCommandsInit:
    def test_commands_importable(self):
        """Test commands package is importable."""
        from minimax_cli import commands
        assert commands is not None
