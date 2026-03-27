"""Tests for minimax_cli.commands.ps module."""

import pytest

class TestPS:
    def test_ps_command_exists(self):
        from minimax_cli.commands.ps import ps
        assert ps is not None

    def test_list_models_command_exists(self):
        from minimax_cli.commands.ps import list_models
        assert list_models is not None

    def test_proc_info_returns_none(self):
        from minimax_cli.commands.ps import _proc_info
        from pathlib import Path
        result = _proc_info(Path("/nonexistent"))
        assert result is None

    def test_gpu_summary_returns_list(self):
        from minimax_cli.commands.ps import _gpu_summary
        result = _gpu_summary()
        assert isinstance(result, list)
