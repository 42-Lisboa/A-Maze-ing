import random
from typing import Any


# =============================================================================
#                               👾 MazeVisualizer 👾
# -----------------------------------------------------------------------------

class MazeVisualizer:
    """Interactive terminal visualizer for the generated maze.

    Attributes:
        runner (Any): MazeRunner that owns the maze and the solver.
        show_path (bool): Whether the shortest path is displayed.
        color_idx (int): Index of the current wall color in the palette.
        colors (list[str]): ANSI color palette used for the walls.
        entry_c (str): ANSI color for the entry cell.
        exit_c (str): ANSI color for the exit cell.
        path_c (str): ANSI color for the solution path.
        pattern_42_c (str): ANSI color for the "42" pattern walls.
        pattern_42_cell_c (str): ANSI color for the "42" pattern cells.
        reset_c (str): ANSI code that resets the terminal color.
    """

    def __init__(self, runner: Any) -> None:
        """Initializes the visualizer state and the color settings.

        Args:
            runner (Any): MazeRunner holding the maze and the solver.
        """
        self.runner = runner
        self.show_path = False
        self.color_idx = 0

        # ANSI color palette for the walls
        self.colors = [
            '\033[97m', '\033[38;5;135m',        # White, Purple
            '\033[38;5;50m', '\033[38;5;39m',   # Turmaline, Blue
            '\033[38;5;218m', '\033[38;5;215m'  # Rose, Soft orange
        ]
        # Solid Block Colors for specific elements
        self.entry_c = '\033[92m'  # Green for Entry
        self.exit_c = '\033[91m'   # Red for Exit
        self.path_c = '\033[93m'   # Bright Yellow for Path

        # Colors for the "42" pattern
        self.pattern_42_c = '\033[38;5;226m'       # BR Yellow (walls)
        self.pattern_42_cell_c = '\033[38;5;35m'   # BR Green (cells)

        self.reset_c = '\033[0m'

    def _clear_screen(self) -> None:
        """Clears the terminal screen using ANSI escape codes."""
        print("\033[H\033[J", end="")

    def _draw_maze(self) -> None:
        """Renders the maze grid as an expanded 2x+1 block matrix."""
        grid = self.runner.maze.grid
        entry = self.runner.maze.maze_entry
        maze_exit = self.runner.maze.maze_exit
        width = len(grid[0])
        height = len(grid)

        # Get the actual coordinates of the 42 pattern from the generator
        coords_42 = self.runner.maze.get_42_coords()

        current_color = self.colors[self.color_idx]

        # 1. Create a visual matrix (2x + 1) fully filled with colored blocks
        vis_height = height * 2 + 1
        vis_width = width * 2 + 1
        wall_blk = f"{current_color}██{self.reset_c}"
        vis = [[wall_blk for _ in range(vis_width)] for _ in range(vis_height)]

        # 2. Carve empty spaces reading the bits from the real maze
        NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
        for y in range(height):
            for x in range(width):
                vy, vx = y * 2 + 1, x * 2 + 1

                # Check if the cell is part of the 42 pattern
                if (x, y) in coords_42:
                    dark_block = f"{self.pattern_42_c}░░{self.reset_c}"
                    cell_block = f"{self.pattern_42_cell_c}██{self.reset_c}"
                    # Paredes (3x3 em volta) em verde escuro...
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            vis[vy + dy][vx + dx] = dark_block
                    # ...e o centro da célula preenchido em amarelo
                    vis[vy][vx] = cell_block
                    continue

                # O centro da célula normal é sempre um corredor aberto
                vis[vy][vx] = "  "

                cell = grid[y][x]
                if (cell & NORTH) == 0:
                    vis[vy - 1][vx] = "  "
                if (cell & SOUTH) == 0:
                    vis[vy + 1][vx] = "  "
                if (cell & EAST) == 0:
                    vis[vy][vx + 1] = "  "
                if (cell & WEST) == 0:
                    vis[vy][vx - 1] = "  "

        # 3. Overlay the solution path (if active)
        if self.show_path:
            path_str = self.runner.solve_maze()
            if path_str:
                px, py = entry
                path_block = f"{self.path_c}🔸{self.reset_c}"
                for move in path_str:
                    if move == 'N':
                        vis[py * 2][px * 2 + 1] = path_block      # Carved wall
                        py -= 1
                    elif move == 'S':
                        vis[py * 2 + 2][px * 2 + 1] = path_block  # Carved wall
                        py += 1
                    elif move == 'E':
                        vis[py * 2 + 1][px * 2 + 2] = path_block  # Carved wall
                        px += 1
                    elif move == 'W':
                        vis[py * 2 + 1][px * 2] = path_block      # Carved wall
                        px -= 1
                    vis[py * 2 + 1][px * 2 + 1] = path_block      # Cell center

        # 4. Mark Entry and Exit by overlapping colors (Solid Blocks)
        ey, ex = entry[1] * 2 + 1, entry[0] * 2 + 1
        vis[ey][ex] = f"{self.entry_c}██{self.reset_c}"

        xy, xx = maze_exit[1] * 2 + 1, maze_exit[0] * 2 + 1
        vis[xy][xx] = f"{self.exit_c}██{self.reset_c}"

        # 5. Print the solid maze
        for row in vis:
            print("".join(row))
        print(f"\n{self.pattern_42_cell_c}=============================== "
              f"{self.reset_c}{self.pattern_42_c}A-Maze-ing{self.reset_c} "
              f"{self.pattern_42_cell_c}==============================="
              f"{self.reset_c}")

    def run(self) -> None:
        """Main interactive menu loop."""
        col = 36  # largura da coluna esquerda do menu

        while True:
            self._clear_screen()
            self._draw_maze()

            print(f"\n{'\033[38;5;39m'}"
                  f"{'1. Re-generate a new maze'.ljust(col)}"
                  "2. Show / Hide the shortest path")
            print(f"{'3. Rotate the wall colours'.ljust(col)}"
                  "4. Break dead-ends (Make it imperfect)")

            choice = input(f"{'\033[38;5;35m'}{'5. Quit'.ljust(col)}"
                           f"{self.reset_c}Choice? (1-5): ").strip()

            if choice == '1':
                # Draw a new seed and recreate the data before generating
                if hasattr(self.runner, 'parsed_data'):
                    self.runner.parsed_data.seed = random.randint(1, 999999)
                self.runner.generate_maze()
                self.runner.export_maze()
            elif choice == '2':
                self.show_path = not self.show_path
            elif choice == '3':
                # Rotates the index to change the walls color
                self.color_idx = (self.color_idx + 1) % len(self.colors)
            elif choice == '4':
                # Breaks extra walls to create loops and updates grid
                self.runner.maze.break_extra_walls_de()
                self.runner.maze.perfect = False
                self.runner.export_maze()
            elif choice == '5':
                print("\nClosing visualizer. Maze saved successfully!")
                break
