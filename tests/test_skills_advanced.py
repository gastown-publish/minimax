"""Advanced tests for skills module."""

import pytest
from pathlib import Path
from unittest.mock import patch


class TestSkillsAdvanced:
    def test_get_skill_path_returns_path(self):
        """Test get_skill_path returns a Path."""
        from minimax_cli.skills import get_skill_path
        path = get_skill_path("test")
        assert isinstance(path, Path)
        assert path.suffix == ".md"

    def test_list_skills_returns_list(self):
        """Test list_skills returns list of dicts."""
        from minimax_cli.skills import list_skills
        result = list_skills()
        assert isinstance(result, list)
        # Each item should have name, title, description, path
        if result:
            assert "name" in result[0]

    def test_load_skill_with_mock(self):
        """Test load_skill loads content."""
        from minimax_cli.skills import load_skill
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value="# Test\nContent"):
                result = load_skill("test")
                assert result == "# Test\nContent"

    def test_load_skill_returns_none_for_missing(self):
        """Test load_skill returns None for missing skill."""
        from minimax_cli.skills import load_skill
        with patch('pathlib.Path.exists', return_value=False):
            result = load_skill("nonexistent")
            assert result is None
