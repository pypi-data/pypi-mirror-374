"""Bricks and Graphs - An agentic framework for multi-block agent decision graphs."""

from typing import Final

__version__: Final[str] = "0.1.1"
__author__: Final[str] = "Igor"
__email__: Final[str] = "igor@example.com"

# Core exports
from . import bricks, core

__all__ = ["__version__", "__author__", "__email__", "core", "bricks"]
