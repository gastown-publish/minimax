"""Tests for term command functions."""

import pytest


class TestTermFuncs:
    def test_term_command_importable(self):
        """Test term command is importable."""
        from minimax_cli.commands import term
        assert term is not None
