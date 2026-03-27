"""Tests for minimax_cli.acp module."""

import pytest


class TestACP:
    """Tests for ACP server module."""

    def test_acp_server_imports(self):
        """Test acp.server module imports."""
        from minimax_cli.acp import server
        assert server is not None

    def test_is_safe_path_function(self):
        """Test _is_safe_path function exists."""
        from minimax_cli.acp.server import _is_safe_path
        assert _is_safe_path is not None

    def test_safe_path_rejects_traversal(self):
        """Test _is_safe_path blocks path traversal."""
        from minimax_cli.acp.server import _is_safe_path
        from pathlib import Path
        
        allowed = Path("/workspace")
        malicious = Path("/workspace/../../../etc/passwd")
        
        result = _is_safe_path(malicious, allowed)
        assert result is False

    def test_safe_path_allows_valid(self):
        """Test _is_safe_path allows valid paths."""
        from minimax_cli.acp.server import _is_safe_path
        from pathlib import Path
        
        allowed = Path("/workspace")
        valid = Path("/workspace/minimax/main.py")
        
        result = _is_safe_path(valid, allowed)
        assert result is True
