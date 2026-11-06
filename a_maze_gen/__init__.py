"""Maze configuration and validation parsing module.

This __init__.py file has the fundamental role of telling Python
that this directory is not just a regular folder, but a modular
and importable package. It provides the `MazeParser` class, which
validates and parses a maze configuration text file using Pydantic.
"""

from .a_maze_gen import MazeGenerator

__all__ = ["MazeGenerator"]
