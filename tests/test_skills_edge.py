"""Edge case tests for skills module."""

import pytest
from pathlib import Path
from unittest.mock import patch


class TestSkillsEdge:
    def test_load_skill_missing(self):
        """Test load_skill returns None for missing skill."""
        from minimax_cli.skills import load_skill
        with patch('pathlib.Path.exists', return_value=False):
            result = load_skill("nonexistent")
            assert result is None

    def test_list_skills_empty_dir(self):
        """Test list_skills handles empty directory."""
        from minimax_cli.skills import list_skills
        with patch('pathlib.Path.glob', return_value=[]):
            result = list_skills()
            assert result == []

    def test_get_skill_path(self):
        """Test get_skill_path returns correct path."""
        from minimax_cli.skills import get_skill_path
        path = get_skill_path("test")
        assert isinstance(path, Path)
        assert path.name == "test.md"
