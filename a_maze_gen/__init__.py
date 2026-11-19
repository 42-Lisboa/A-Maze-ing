"""Reusable maze generation module.

Generates mazes with a Depth-First Search, optionally imperfect (with
loops), and solves them with a Breadth-First Search.

Example:
    from a_maze_gen import MazeGenerator

    maze = MazeGenerator(width=20, height=15, maze_entry=(0, 14),
                         maze_exit=(19, 0), output_file="maze.txt",
                         perfect=True, seed=42)
    grid = maze.generate()   # list of rows, one hex-bit int per cell
    path = maze.solve()      # e.g. 'NNEESW', or None if no path
"""

from .a_maze_gen import MazeGenerator

__all__ = ["MazeGenerator"]
