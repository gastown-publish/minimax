"""Tests for minimax_cli.skills module."""

import pytest
from pathlib import Path


class TestSkills:
    """Tests for skills module."""

    def test_skills_module_imports(self):
        """Test skills module imports."""
        from minimax_cli import skills
        assert skills is not None

    def test_skills_directory_exists(self):
        """Test skills directory is configured."""
        from minimax_cli.skills import SKILLS_DIR
        assert SKILLS_DIR is not None

    def test_skill_files_exist(self):
        """Test all skill files exist."""
        from minimax_cli.skills import SKILLS_DIR
        
        expected = ["write-tests.md", "fix-tests.md", "ralph-loop.md", "refactor.md"]
        for skill in expected:
            assert (SKILLS_DIR / skill).exists()

    def test_skill_files_have_content(self):
        """Test skill files are not empty."""
        from minimax_cli.skills import SKILLS_DIR
        
        for md_file in SKILLS_DIR.glob("*.md"):
            content = md_file.read_text()
            assert len(content) > 0
