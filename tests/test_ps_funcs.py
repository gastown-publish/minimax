"""Tests for ps command functions."""

import pytest


class TestPsFuncs:
    def test_ps_command_importable(self):
        """Test ps command is importable."""
        from minimax_cli.commands import ps
        assert ps is not None

    def test_proc_info_importable(self):
        """Test _proc_info is importable."""
        from minimax_cli.commands.ps import _proc_info
        assert callable(_proc_info)

    def test_gpu_summary_importable(self):
        """Test _gpu_summary is importable."""
        from minimax_cli.commands.ps import _gpu_summary
        assert callable(_gpu_summary)

    def test_is_server_env_importable(self):
        """Test _is_server_env is importable."""
        from minimax_cli.commands.ps import _is_server_env
        assert callable(_is_server_env)
