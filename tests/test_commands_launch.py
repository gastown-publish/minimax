"""Tests for minimax_cli.commands.launch module."""

import pytest

class TestLaunch:
    def test_launch_command_exists(self):
        from minimax_cli.commands.launch import launch
        assert launch is not None

    def test_check_api_function(self):
        from minimax_cli.commands.launch import _check_api
        assert _check_api is not None
