"""Tests for minimax_cli.commands.term module."""

import pytest


class TesttermCmd:
    """Tests for term command."""

    def test_command_exists(self):
        """Test term command is registered."""
        from minimax_cli.commands.term import term
        assert term is not None
