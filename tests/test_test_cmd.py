"""Tests for minimax_cli.commands.test_cmd module."""

import pytest


class TestTestCmd:
    """Tests for test command."""

    def test_test_command_exists(self):
        """Test test command is registered."""
        from minimax_cli.commands.test_cmd import test
        assert test is not None
