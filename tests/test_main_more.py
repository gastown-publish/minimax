"""More tests for main.py functions."""

import pytest


class TestMainMore:
    def test_completion_zsh_importable(self):
        """Test completion_zsh is importable."""
        from minimax_cli.main import completion_zsh
        assert completion_zsh is not None

    def test_completion_fish_importable(self):
        """Test completion_fish is importable."""
        from minimax_cli.main import completion_fish
        assert completion_fish is not None

    def test_completion_install_importable(self):
        """Test completion_install is importable."""
        from minimax_cli.main import completion_install
        assert completion_install is not None

    def test_upgrade_importable(self):
        """Test upgrade is importable."""
        from minimax_cli.main import upgrade
        assert upgrade is not None
