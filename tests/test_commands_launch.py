"""Tests for minimax_cli.commands.launch module."""

import pytest


class TestLaunch:
    """Tests for launch command."""

    def test_launch_command_exists(self):
        """Test launch command is registered."""
        from minimax_cli.commands.launch import launch
        assert launch is not None


class TestLaunchFunctions:
    """Tests for launch module functions."""

    def test_check_api_function(self):
        """Test _check_api function exists."""
        from minimax_cli.commands.launch import _check_api
        assert _check_api is not None

    def test_mm_claude_config_path(self):
        """Test MM_CLAUDE_CONFIG is defined."""
        from minimax_cli.commands.launch import MM_CLAUDE_CONFIG
        assert MM_CLAUDE_CONFIG is not None
