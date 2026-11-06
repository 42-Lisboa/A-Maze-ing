import sys
from a_maze_parser import MazeParser, parse_config_file
from a_maze_gen import MazeGenerator
from pydantic import ValidationError


# =============================================================================
#                               🗡️ MazeRunner 🗡️
# -----------------------------------------------------------------------------

class MazeRunner:
    def __init__(self,
                 config_file: str,
                 parsed_data: MazeParser | None = None,
                 maze: MazeGenerator | None = None):
        self.config_file = config_file
        self.parsed_data = parsed_data
        self.maze = maze

    # ========= 1. Method to read config_file.txt and parse the data =========

    def load_config(self) -> MazeParser | None:
        try:
            self.parsed_data = parse_config_file(self.config_file)
            return self.parsed_data
        except ValidationError as e:
            print(f"❌ ValidationError: '{e}'")
            return None

    # ========= 2. Method to read config_file.txt and parse the data =========

    def generate_maze(self) -> list[list[int]] | None:
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
