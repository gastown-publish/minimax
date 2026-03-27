"""Tests for minimax_cli.__init__ module."""

import pytest


class TestInit:
    """Tests for package init."""

    def test_version_defined(self):
        """Test __version__ is defined."""
        from minimax_cli import __version__
        assert __version__ is not None
        assert isinstance(__version__, str)
