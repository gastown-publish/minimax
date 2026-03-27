"""Tests for minimax_cli.commands.skills_cmd module."""

import pytest

class TestSkills:
    def test_skills_command_exists(self):
        from minimax_cli.commands.skills_cmd import skills
        assert skills is not None
