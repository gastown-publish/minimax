"""Tests for skills_cmd functions."""

import pytest


class TestSkillsCmd:
    def test_skills_cmd_importable(self):
        """Test skills_cmd is importable."""
        from minimax_cli.commands import skills_cmd
        assert skills_cmd is not None

    def test_skills_importable(self):
        """Test skills is importable."""
        from minimax_cli.commands.skills_cmd import skills
        assert skills is not None

    def test_list_skills_importable(self):
        """Test list_skills is importable."""
        from minimax_cli.commands.skills_cmd import list_skills
        assert list_skills is not None

    def test_run_skill_importable(self):
        """Test run_skill is importable."""
        from minimax_cli.commands.skills_cmd import run_skill
        assert run_skill is not None
