import sys
import time
from a_maze_parser import MazeParser, parse_config_file
from a_maze_gen import MazeGenerator
from a_maze_vis import MazeVisualizer
from pydantic import ValidationError

NORTH = 1 << 0  # Binary: 0001 (Decimal: 1)
EAST = 1 << 1  # Binary: 0010 (Decimal: 2)
SOUTH = 1 << 2  # Binary: 0100 (Decimal: 4)
WEST = 1 << 3  # Binary: 1000 (Decimal: 8)


# =============================================================================
#                               ▶️ MazeRunner ▶️
# -----------------------------------------------------------------------------

class MazeRunner:
    """Orchestrates maze parsing, generation, solving, and exporting.

    Attributes:
        config_file (str): Path to the configuration text file.
        parsed_data (MazeParser | None): Validated configuration data.
        maze (MazeGenerator | None): The maze generation engine instance.
    """
    def __init__(self,
                 config_file: str,
                 parsed_data: MazeParser | None = None,
                 maze: MazeGenerator | None = None):
        self.config_file = config_file
        self.parsed_data = parsed_data
        self.maze = maze

    # ========= 1. Method to read config_file.txt and parse the data =========

    def load_config(self) -> MazeParser | None:
        """Reads and validates the configuration file using Pydantic.

        Returns:
            MazeParser | None: The validated data object, or None if it fails.
        """
        try:
            self.parsed_data = parse_config_file(self.config_file)
            return self.parsed_data
        except ValidationError as e:
            print(f"❌ ValidationError: '{e}'")
            return None

    # ====== 2. Method to use the MazeGenerator object to build the maze ======

    def generate_maze(self) -> list[list[int]] | None:
        """Instantiates the generator and carves the maze grid paths.

        Returns:
            list[list[int]] | None: The generated maze grid, or None if
            missing data.
        """
        if self.parsed_data:
            # .model_dump() pydantic method to transform the object into a dict
            self.maze = MazeGenerator(**self.parsed_data.model_dump())

            self.maze.create_closed_cells()
            self.maze.maze_digger(start=self.maze.maze_entry)
            if not self.maze.perfect:
                self.maze.break_extra_walls_de()

            return self.maze.grid
        else:
            # Return an empty grid (or raise an exception) if parsing failed
            print("❌ Cannot generate maze: Configuration data is missing.")
            return None

    # ============ 3. Method to solve the generated maze using BFS ============

    def solve_maze(self) -> str | None:
        """Finds the shortest path from entry to exit using BFS: Breadth-First
        Search.

        Returns:
            str | None: The solution path string (e.g., 'EESW'), or None if no
            path.
        """
        if self.maze:

            # 🔸 Save 42 blocked cells on visited and begin BFS maze search
            visited_cells = self.maze.get_42_coords()
            queue = [(self.maze.maze_entry, "")]  # coords + path trace

            while queue:

                # 🔸 Pop a cell from the front of queue and check if it's exit
                cell = queue.pop(0)
                if cell[0] == self.maze.maze_exit:
                    return cell[1]  # returns the path trace

                # 🔸 Unpack cell so we can calculate neighbors coords
                x, y = cell[0]
                path_trace = cell[1]

                # 🔸 For each open direction we add neighbors coords + trace
                if (self.maze.grid[y][x] & NORTH) == 0:
                    n_cell = (x, y - 1)
                    if n_cell not in visited_cells:
                        visited_cells.add(n_cell)
                        queue.append((n_cell, path_trace + "N"))

                if (self.maze.grid[y][x] & EAST) == 0:
                    n_cell = (x + 1, y)
                    if n_cell not in visited_cells:
                        visited_cells.add(n_cell)
                        queue.append((n_cell, path_trace + "E"))

                if (self.maze.grid[y][x] & SOUTH) == 0:
                    n_cell = (x, y + 1)
                    if n_cell not in visited_cells:
                        visited_cells.add(n_cell)
                        queue.append((n_cell, path_trace + "S"))

                if (self.maze.grid[y][x] & WEST) == 0:
                    n_cell = (x - 1, y)
                    if n_cell not in visited_cells:
                        visited_cells.add(n_cell)
                        queue.append((n_cell, path_trace + "W"))

        return None

    # ========= 4. Method to export the generated maze to a .txt file =========

    def export_maze(self) -> None:
        """Exports the maze matrix, coords., and solution path to a file."""
        if self.parsed_data and self.maze:
            try:
                with open(self.parsed_data.output_file, 'w') as file:
                    for row in self.maze.grid:
                        for cell in row:
                            file.write(f"{cell:x}")
                        file.write('\n')
                    file.write(
                               f"\n{self.maze.maze_entry[0]},"
                               f"{self.maze.maze_entry[1]}      # entry (x,y)"
                               f"\n{self.maze.maze_exit[0]},"
                               f"{self.maze.maze_exit[1]}       # exit  (x,y)")
                    path_trace_solution = self.solve_maze()
                    if path_trace_solution:
                        file.write(f"\n{path_trace_solution}\n")
            except OSError as e:
                print(f"❌ Error saving the maze to "
                      f"'{self.parsed_data.output_file}': {e}")

    # ===================== 5. Main Orchestration Method =====================

    def run(self) -> None:
        """Orchestrates the entire execution flow of the:
                                                        ✅ MazeParser
                                                        🧱 MazeGenerator
                                                        ▶️ MazeRunner
                                                        👾 MazeVisualizer."""

        # Load and validate configuration
        print("✅ Starting MazeParser...")
        if not self.load_config():
            print("🛑 Execution stopped: Configuration failed.")
            return
        print(" 🔹 Configuration loaded successfully.")

        # Generate the maze matrix and carve paths
        print("🧱 Starting MazeGenerator...")
        if not self.generate_maze():
            print("🛑 Execution stopped: Maze generation failed.")
            return
        print(" 🔹 Maze generated.")

        # Export the maze to .txt (this internally calls solve_maze)
        print("▶️  Starting MazeRunner...")
        self.export_maze()
        if self.parsed_data:
            print(" 🔹 Maze successfully saved to "
                  f"'{self.parsed_data.output_file}'.")

        # Now let's visualize all
        print("👾 Starting MazeVisualizer...")
        time.sleep(10)
        visualizer = MazeVisualizer(runner=self)
        visualizer.run()


# ============================== Program Test ================================

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("❌ Error: Invalid number of arguments.")
        print("💡 Usage: python3 a_maze_ing.py <config_file.txt>")
        sys.exit(1)

    config_arg = sys.argv[1]

    runner = MazeRunner(config_file=config_arg)
    runner.run()
