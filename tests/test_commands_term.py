"""Tests for minimax_cli.commands.term module."""

import pytest

class TestTerm:
    def test_term_command_exists(self):
        from minimax_cli.commands.term import term
        assert term is not None
