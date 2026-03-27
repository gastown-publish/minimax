"""Tests for skills module functions."""

import pytest


class TestSkills:
    def test_list_skills_importable(self):
        """Test list_skills is importable."""
        from minimax_cli.skills import list_skills
        assert callable(list_skills)

    def test_load_skill_importable(self):
        """Test load_skill is importable."""
        from minimax_cli.skills import load_skill
        assert callable(load_skill)
