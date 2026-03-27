"""Edge case tests for ACP module."""

import pytest
from pathlib import Path
from unittest.mock import patch


class TestACPEdge:
    def test_is_safe_path_valid(self):
        """Test _is_safe_path allows valid paths."""
        from minimax_cli.acp.server import _is_safe_path
        allowed = Path("/tmp")
        result = _is_safe_path(Path("/tmp/test"), allowed)
        assert result == True

    def test_is_safe_path_invalid(self):
        """Test _is_safe_path rejects invalid paths."""
        from minimax_cli.acp.server import _is_safe_path
        allowed = Path("/tmp")
        result = _is_safe_path(Path("/etc/passwd"), allowed)
        assert result == False

    def test_build_system_prompt_returns_string(self):
        """Test _build_system_prompt returns string."""
        from minimax_cli.acp.server import _build_system_prompt
        result = _build_system_prompt()
        assert isinstance(result, str)
        assert len(result) > 0
