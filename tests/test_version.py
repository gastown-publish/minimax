"""Tests for minimax_cli version."""
import pytest

class TestVersion:
    def test_version_defined(self):
        from minimax_cli import __version__
        assert __version__ is not None
        assert isinstance(__version__, str)
