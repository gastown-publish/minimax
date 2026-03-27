from __future__ import annotations
__all__ = ["__version__"]

"""mm — MiniMax-M2.5 AI terminal agent."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("minimax-agent")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
