"""Tests for __init__ and __main__ modules."""

import pytest


class TestInitMain:
    def test_version_importable(self):
        """Test __version__ is importable."""
        from minimax_cli import __version__
        assert isinstance(__version__, str)

    def test_main_module_importable(self):
        """Test main module is importable."""
        from minimax_cli import main
        assert main is not None
