"""Tests for minimax_cli.commands.loop module."""

import pytest

class TestLoop:
    def test_loop_command_exists(self):
        from minimax_cli.commands.loop import loop
        assert loop is not None
