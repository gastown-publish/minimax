from __future__ import annotations
"""mm — MiniMax-M2.5 AI terminal agent."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("minimax-agent")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
