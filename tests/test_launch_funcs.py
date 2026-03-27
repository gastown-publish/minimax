"""Tests for launch command functions."""

import pytest


class TestLaunchFuncs:
    def test_launch_command_importable(self):
        """Test launch command is importable."""
        from minimax_cli.commands import launch
        assert launch is not None

    def test_check_api_importable(self):
        """Test _check_api is importable."""
        from minimax_cli.commands.launch import _check_api
        assert callable(_check_api)

    def test_require_key_importable(self):
        """Test _require_key is importable."""
        from minimax_cli.commands.launch import _require_key
        assert callable(_require_key)

    def test_has_docker_importable(self):
        """Test _has_docker is importable."""
        from minimax_cli.commands.launch import _has_docker
        assert callable(_has_docker)
