from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator)


# =============================================================================
#                               ✅ MazeParser ✅
# -----------------------------------------------------------------------------

class MazeParser(BaseModel):
    """Parses and validates maze configuration parameters through Pydantic.

    Attributes:
        width (int): The width of the maze (minimum 9, maximum 50).
        height (int): The height of the maze (minimum 7, maximum 50).
        maze_entry (tuple[int, int]): The (x, y) coord. for the maze entry.
        maze_exit (tuple[int, int]): The (x, y) coord. for the maze exit.
        output_file (str): The name of the output text file.
        perfect (bool): True for a perfect maze, False for a playable board.
        seed (int): The seed used for random maze generation.
    """
    width: int = Field(ge=9, le=50, alias="WIDTH")
    height: int = Field(ge=7, le=50, alias="HEIGHT")
    maze_entry: tuple[int, int] = Field(alias="ENTRY")
    maze_exit: tuple[int, int] = Field(alias="EXIT")
    output_file: str = Field(alias="OUTPUT_FILE")
    perfect: bool = Field(default=False, alias="PERFECT")
    seed: int | None = Field(default=None, alias="SEED")

    # ======== 1. Validator method to check correct tuple coordinates ========

    @field_validator('maze_entry', 'maze_exit', mode='before')
    @classmethod
    def validate_coordinates(cls, coord: str) -> tuple[int, int]:
        """Validates and converts a coordinate string into a tuple.

        Args:
            coord (str): The raw coordinate string (e.g., '0,0').

        Returns:
            tuple[int, int]: The parsed (x, y) integer coordinates.

        Raises:
            ValueError: If the format is invalid or values are negative.
        """
        if not isinstance(coord, str) or ',' not in coord:
            raise ValueError("The coordinate must be a string "
                             "separated by a comma ie: '0,0'")

        coord_cleaned = "".join(coord.split())  # remove white spaces
        coord_final = coord_cleaned.split(',')  # split only values into a list
        if len(coord_final) != 2:
            raise ValueError("Coordinate must have only two integers")

        try:
            x = int(coord_final[0])  # now we convert str value to integer
            y = int(coord_final[1])  # now we convert str value to integer
        except ValueError:
            raise ValueError("Coordinates must be valid integers")

        if x < 0 or y < 0:
            raise ValueError("Coordinates cannot be negative values")

        return (x, y)

    # =========== 2. Validator method for entry/exit maze position ===========

    def get_42_coords(self) -> set[tuple[int, int]]:
        """Calculates the grid coordinates for the '42' blocked pattern.

        Returns:
            set[tuple[int, int]]: A set of (x, y) blocked coordinates.
        """
        pattern_width, pattern_height = 7, 5

        start_x_pattern = (self.width - pattern_width) // 2
        start_y_pattern = (self.height - pattern_height) // 2

        # Matriz local do "42" (relativa ao bloco 7x5):
        # 1 = célula fechada, 0 = espaço
        pattern_grid = [
            [1, 0, 1,  0,  1, 1, 1],
            [1, 0, 1,  0,  0, 0, 1],
            [1, 1, 1,  0,  1, 1, 1],
            [0, 0, 1,  0,  1, 0, 0],
            [0, 0, 1,  0,  1, 1, 1],
        ]
        coords_42 = set()
        for dy, row in enumerate(pattern_grid):
            # ie: where dy = 0, row = [1, 0, 1,  0,  1, 1, 1]
            for dx, cell in enumerate(row):
                # ie: where dx = 0, cell = 1
                if cell == 1:
                    coords_42.add((start_x_pattern + dx, start_y_pattern + dy))

        return coords_42

    @model_validator(mode='after')
    def check_entry_exit_coords(self) -> 'MazeParser':
        """Validates entry and exit positions within the maze limits.

        Ensures coordinates are within grid bounds, not overlapping each
        other, and not placed inside the blocked '42' pattern.

        Returns:
            MazeParser: The validated class instance.

        Raises:
            ValueError: If coordinates are out of bounds or overlapping.
        """
        entry_x, entry_y = self.maze_entry
        exit_x, exit_y = self.maze_exit

        if entry_x >= self.width:
            raise ValueError(f"The entry X value ({entry_x}) "
                             f"is out of the grid (max {self.width-1})")
        if entry_y >= self.height:
            raise ValueError(f"The entry Y value ({entry_y}) "
                             f"is out of the grid (max {self.height-1})")
        if exit_x >= self.width:
            raise ValueError(f"The exit X value ({exit_x}) "
                             f"is out of the grid (max {self.width-1})")
        if exit_y >= self.height:
            raise ValueError(f"The exit Y value ({exit_y}) "
                             f"is out of the grid (max {self.height-1})")

        # Entry and exit cannot exist in the same spot
        if self.maze_entry == self.maze_exit:
            raise ValueError("Entry and exit coordinates must be different")

        # Now we check if entry or exit are in the 42 blocked cells
        blocked_coords = self.get_42_coords()
        if self.maze_entry in blocked_coords:
            raise ValueError(f"Entry position {self.maze_entry} "
                             "overlaps with the '42' wall pattern")
        if self.maze_exit in blocked_coords:
            raise ValueError(f"Exit position {self.maze_exit} "
                             "overlaps with the '42' wall pattern")

        return self

    # ============== 3. Validator method for output file format ==============

    @field_validator('output_file')
    @classmethod
    def ends_with_txt(cls, value: str) -> str:
        """Validates that the output file contains a .txt extension.

        Args:
            value (str): The target output file name.

        Returns:
            str: The validated file name.

        Raises:
            ValueError: If the file does not end with '.txt'.
        """
        if not value.endswith('.txt'):
            raise ValueError("Output file must be a .txt")
        if ' ' in value:
            value_cleaned = "".join(value.split())
            return value_cleaned
        return value


# =============================================================================
#                      ✅ Config file Parser function ✅
# -----------------------------------------------------------------------------

def parse_config_file(file_name: str) -> MazeParser | None:
    """Reads and parses the maze configuration from a text file.

    Args:
        file_name (str): The path to the configuration text file.

    Returns:
        MazeParser | None: A validated MazeParser object if successful,
        or None if the file cannot be opened.
    """
    try:
        with open(file_name, 'r') as file:  # Open the file
            config_txt = file.read()  # Read the content to our variable
            config_txt_lines = config_txt.splitlines()  # make it list of lines
            config_keys: dict[str, str] = {}
            for line in config_txt_lines:
                if not line.startswith('#') and '=' in line:
                    key, value = line.split('=')
                    config_keys[key.strip()] = value.strip()  # - extra spaces
            return MazeParser(**config_keys)  # type: ignore

    except OSError as e:  # Operating System Error
        print(f"Error opening file '{file_name}': {e}")
        return None


# ============================== Program Test ================================

if __name__ == "__main__":
    print("=== Starting MazeParser test ===\n")

    # Make sure you have a 'config.txt' file in the same folder as the script
    parsed_data = parse_config_file('config.txt')

    if parsed_data:
        print("✅ File successfully read and validated!\n")

        # Prints the entire model with all structured fields
        print(parsed_data)

        # Proof that the conversion worked and is ready for the matrix
        print(f"\nStructured entry type: {type(parsed_data.maze_entry)}")
        print(f"Exit values: {parsed_data.maze_exit}")
    else:
        print("❌ Failed to process the configuration file.")
