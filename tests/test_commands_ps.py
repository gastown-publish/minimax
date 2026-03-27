"""Tests for minimax_cli.commands.ps module."""

import pytest


class TestPS:
    """Tests for ps command functions."""

    def test_ps_command_exists(self):
        """Test ps command is registered."""
        from minimax_cli.commands.ps import ps
        assert ps is not None

    def test_list_models_command_exists(self):
        """Test list command is registered."""
        from minimax_cli.commands.ps import list_models
        assert list_models is not None

    def test_proc_info_returns_none_for_missing_pid(self):
        """Test _proc_info returns None for non-existent PID file."""
        from minimax_cli.commands.ps import _proc_info
        from pathlib import Path
        
        result = _proc_info(Path("/nonexistent/pid.file"))
        assert result is None

    def test_gpu_summary_returns_list(self):
        """Test _gpu_summary returns a list."""
        from minimax_cli.commands.ps import _gpu_summary
        
        result = _gpu_summary()
        assert isinstance(result, list)


class TestListModels:
    """Tests for list_models command."""

    def test_list_models_function_exists(self):
        """Test list_models function exists."""
        from minimax_cli.commands.ps import list_models
        assert list_models is not None
