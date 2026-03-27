"""Bundled skills — prompt templates for the MiniMax agent."""

from __future__ import annotations

__all__ = ["get_skill_path", "list_skills", "load_skill"]

from pathlib import Path


SKILLS_DIR = Path(__file__).parent


def get_skill_path(name: str) -> Path:
    """Return the full path to a skill file."""
    return SKILLS_DIR / f"{name}.md"


def list_skills() -> list[dict]:
    """Return metadata for all bundled skills."""
    skills = []
    for path in sorted(SKILLS_DIR.glob("*.md")):
        name = path.stem
        # Read first line as title, second paragraph as description
        text = path.read_text()
        lines = text.strip().splitlines()
        title = lines[0].lstrip("# ").strip() if lines else name
        desc = ""
        for line in lines[1:]:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("---"):
                desc = line
                break
        skills.append({"name": name, "title": title, "description": desc, "path": str(path)})
    return skills


def load_skill(name: str) -> str | None:
    """Load a skill's prompt template by name."""
    path = get_skill_path(name)
    if path.exists():
        return path.read_text()
    return None
