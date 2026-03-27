"""Tests for minimax_cli.commands.launch module."""

import pytest


class TestLaunchCmd:
    """Tests for launch command."""

    def test_launch_command_exists(self):
        """Test launch command is registered."""
        from minimax_cli.commands.launch import launch
        assert launch is not None
