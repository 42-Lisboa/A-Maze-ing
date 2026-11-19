import sys
import time
from a_maze_parser import MazeParser, parse_config_file
from a_maze_gen import MazeGenerator
from a_maze_vis import MazeVisualizer
from pydantic import ValidationError


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
            try:
                # .model_dump() pydantic method to transform object into a dict
                self.maze = MazeGenerator(**self.parsed_data.model_dump())
            except ValueError as e:
                print(f"❌ Invalid maze settings: {e}")
                return None
            return self.maze.generate()
        else:
            # Return an empty grid (or raise an exception) if parsing failed
            print("❌ Cannot generate maze: Configuration data is missing.")
            return None

    # ============ 3. Method to solve the generated maze using BFS ============

    def solve_maze(self) -> str | None:
        """Finds the shortest path from entry to exit using the generator.

        Returns:
            str | None: The solution path string (e.g., 'EESW'), or None if no
            path.
        """
        if self.maze:
            return self.maze.solve()
        return None

    # ========= 4. Method to export the generated maze to a .txt file =========

    def export_maze(self) -> bool:
        """Exports the maze matrix, coords., and solution path to a file.

        Returns:
            bool: True if the file was saved, False otherwise.
        """
        if not (self.parsed_data and self.maze):
            return False
        try:
            with open(self.parsed_data.output_file, 'w') as file:
                for row in self.maze.grid:
                    for cell in row:
                        file.write(f"{cell:x}")
                    file.write('\n')
                file.write(
                            f"\n{self.maze.maze_entry[0]},"
                            f"{self.maze.maze_entry[1]}"
                            f"\n{self.maze.maze_exit[0]},"
                            f"{self.maze.maze_exit[1]}")
                path_trace_solution = self.solve_maze()
                if path_trace_solution:
                    file.write(f"\n{path_trace_solution}\n")
        except OSError as e:
            print(f"❌ Error saving the maze to "
                  f"'{self.parsed_data.output_file}': {e}")
            return False
        return True

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
        if self.parsed_data and (self.parsed_data.width < 9
                                 or self.parsed_data.height < 7):
            print("⚠️ Maze too small for the '42' pattern: it was omitted.")

        # Generate the maze matrix and carve paths
        print("🧱 Starting MazeGenerator...")
        if not self.generate_maze():
            print("🛑 Execution stopped: Maze generation failed.")
            return
        print(" 🔹 Maze generated.")

        # Export the maze to .txt (this internally calls solve_maze)
        print("▶️  Starting MazeRunner...")
        if not self.export_maze():
            print("🛑 Execution stopped: Maze could not be saved.")
            return
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
    try:
        runner.run()
    except (KeyboardInterrupt, EOFError):
        print("\033[0m\n👋 Interrupted. Bye!")
        sys.exit(0)
