import random

NORTH = 1 << 0  # Binary: 0001 (Decimal: 1)
EAST = 1 << 1  # Binary: 0010 (Decimal: 2)
SOUTH = 1 << 2  # Binary: 0100 (Decimal: 4)
WEST = 1 << 3  # Binary: 1000 (Decimal: 8)


# =============================================================================
#                               🧱 MazeGenerator 🧱
# -----------------------------------------------------------------------------

class MazeGenerator:
    """Generates a maze using Depth-First Search and specific constraints.

    Attributes:
        width (int): The width of the maze grid.
        height (int): The height of the maze grid.
        maze_entry (tuple[int, int]): The (x, y) entry coordinates.
        maze_exit (tuple[int, int]): The (x, y) exit coordinates.
        output_file (str): The filename for exporting the maze data.
        perfect (bool): True - perfect maze (one path), False - playable board.
        seed (int | None): The random seed for reproducible maze generation.
        grid (list[list[int]]): The 2D matrix representing the maze cells.
    """
    def __init__(
            self,
            width: int, height: int, maze_entry: tuple[int, int],
            maze_exit: tuple[int, int], output_file: str,
            perfect: bool = False, seed: int | None = None):
        self.width = width
        self.height = height
        self.maze_entry = maze_entry
        self.maze_exit = maze_exit
        self.output_file = output_file
        self.perfect = perfect
        self.seed = seed
        self.grid: list[list[int]] = []

    # ================= 1. Create Maze with all cells closed =================

    def create_closed_cells(self) -> list[list[int]]:
        """Initializes the maze grid with all walls closed.

        Each cell is initialized with the value 15 (binary 1111), meaning
        all four walls (North, East, South, West) are solid.

        Returns:
            list[list[int]]: The generated 2D grid matrix.
        """
        for _ in range(self.height):
            current_row: list[int] = []
            self.grid.append(current_row)
            for _ in range(self.width):
                current_row.append(15)
        return self.grid

    # ============== 2. Get 42 coordinates blocked cells pattern ==============

    def get_42_coords(self) -> set[tuple[int, int]]:
        """Calculates the coordinates of the centered '42' blocked pattern.

        Returns:
            set[tuple[int, int]]: A set of (x, y) coordinates from the '42'.
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

    # ================ 3. Method to validate cell coordinates ================

    def is_neighbor_coords_valid(self,
                                 neighbor_cell_coords: tuple[int, int],
                                 visited_cells: set[tuple[int, int]]) -> bool:
        """Checks if a neighbor cell is within the grid limits and unvisited.

        Args:
            neighbor_cell_coords (tuple[int, int]): The coordinates to check.
            visited_cells (set[tuple[int, int]]): Set of already visited cells.

        Returns:
            bool: True- cell is valid and hasn't been visited, False otherwise.
        """
        x, y = neighbor_cell_coords
        if neighbor_cell_coords in visited_cells:
            return False
        if x >= 0 and y >= 0 and x < self.width and y < self.height:
            return True
        else:
            return False

    # ========= 4. Dig the perfect Maze using DFS-Depth First Search =========

    def maze_digger(self, start: tuple[int, int]) -> None:
        """Carves the maze paths using an iterative Depth-First Search (DFS)
        algorithm.

        Args:
            start (tuple[int, int]): The (x, y) starting coordinates for the
            excavation.
        """
        # 🔸 If is not 'None', we tell the function to use a seed

        if self.seed:
            random.seed(self.seed)

        # 🔸 Create a compass ruler when moving each direction
        # (changer_x, changer_y, delete_wall_here, delete_wall_there)

        compass: list[tuple] = [
            (0, -1, NORTH, SOUTH),  # N rule
            (+1, 0, EAST, WEST),    # E rule
            (0, +1, SOUTH, NORTH),  # S rule
            (-1, 0, WEST, EAST)     # W rule
        ]

        # 🔸 Save 42 blocked pattern on visited cells and begin DFS maze dig

        visited_cells = self.get_42_coords()
        stack = [start]

        while stack:
            x, y = stack[-1]  # we unpack last cell from stack
            visited_cells.add((x, y))
            random.shuffle(compass)
            for changer_x, changer_y, d_wall_here, d_wall_there in compass:
                n_x = x + changer_x  # n - neighbor
                n_y = y + changer_y  # n - neighbor
                neighbor_cell = (n_x, n_y)
                if self.is_neighbor_coords_valid(neighbor_cell, visited_cells):
                    self.grid[y][x] = self.grid[y][x] & ~ d_wall_here
                    self.grid[n_y][n_x] = self.grid[n_y][n_x] & ~ d_wall_there
                    stack.append((n_x, n_y))
                    break  # to stop compass for loop
            else:
                stack.pop()  # to remove already "finished" cell and trace back

    # ===== 5. Function to check if there is big pools on Imperfect Mazes =====

    def has_3x3_pool(self) -> bool:
        """Checks if the maze contains any 3x3 open areas.

        A pool is defined as a 3x3 block of cells with no internal walls
        dividing them.

        Returns:
            bool: True if at least one 3x3 pool is detected, False otherwise.
        """
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                has_wall = False
                for dy in range(3):  # y movement (Δy)
                    grid_y = y + dy
                    for dx in range(3):  # x movement (Δx)
                        grid_x = x + dx
                        if self.grid[grid_y][grid_x] & EAST == 2 and dx < 2:
                            has_wall = True
                            break
                        if self.grid[grid_y][grid_x] & SOUTH == 4 and dy < 2:
                            has_wall = True
                            break
                    if has_wall:
                        break
            if not has_wall:
                return True
        return False

    # =================== 6. Break extra walls on dead-ends ===================

    def break_extra_walls_de(self) -> None:
        """Breaks extra walls in dead-end cells to create an imperfect,
        playable maze.

        Ensures that removing walls does not create illegal 3x3 open pools
        or break into the protected '42' pattern blocks.
        """

        # 🔸 Create a compass ruler when moving each direction
        # (changer_x, changer_y, delete_wall_here, delete_wall_there)

        compass: list[tuple] = [
            (0, -1, NORTH, SOUTH),  # N rule
            (+1, 0, EAST, WEST),    # E rule
            (0, +1, SOUTH, NORTH),  # S rule
            (-1, 0, WEST, EAST)     # W rule
        ]

        # 🔸 We check which walls to remove only from dead-end cells (3 walls)

        walls_2_remove: list[tuple] = []
        blocked_cells = self.get_42_coords()

        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell.bit_count() != 3:
                    continue
                elif cell & NORTH == 1:
                    walls_2_remove.append(compass[0])
                elif cell & EAST == 2:
                    walls_2_remove.append(compass[1])
                elif cell & SOUTH == 4:
                    walls_2_remove.append(compass[2])
                elif cell & WEST == 8:
                    walls_2_remove.append(compass[3])

                # 🔸 Now as soon one wall is validated we remove it

                random.shuffle(walls_2_remove)
                for changer_x, changer_y, \
                        d_wall_here, d_wall_there in walls_2_remove:
                    n_y = y + changer_y  # n - neighbor
                    n_x = x + changer_x  # n - neighbor
                    neighbor = (n_x, n_y)
                    if self.is_neighbor_coords_valid(neighbor, blocked_cells):
                        self.grid[y][x] = \
                            self.grid[y][x] & ~ d_wall_here
                        self.grid[n_y][n_x] = \
                            self.grid[n_y][n_x] & ~ d_wall_there

                        # 🔸 If the wall removed create a big pool we rebuilt it

                        if self.has_3x3_pool():
                            self.grid[y][x] = \
                                self.grid[y][x] | d_wall_here
                            self.grid[n_y][n_x] = \
                                self.grid[n_y][n_x] | d_wall_there
                            continue
                        else:
                            break


# ============================== Program Test ================================

if __name__ == "__main__":
    print("=== Starting MazeGenerator Test ===\n")

    # 1. Mocking the data that would normally come from your MazeParser
    test_width = 20
    test_height = 15
    test_entry = (0, 14)
    test_exit = (19, 0)

    maze = MazeGenerator(
        width=test_width,
        height=test_height,
        maze_entry=test_entry,
        maze_exit=test_exit,
        output_file="test_maze.txt",
        perfect=False,  # Set to False to test the Pac-Man mode
        seed=13
    )

    # 2. Executing the generation pipeline step by step
    print("🧱 Initializing closed grid...")
    maze.create_closed_cells()
    print(f"Grid created: {len(maze.grid)} rows by "
          f"{len(maze.grid[0])} columns.\n")

    print("⛏️  Digging the perfect maze (DFS)...")
    maze.maze_digger(start=maze.maze_entry)
    print("DFS digging completed.\n")

    if not maze.perfect:
        print("🔨 PERFECT=False detected. Breaking extra "
              "walls to remove dead-ends...")
        maze.break_extra_walls_de()
        print("Extra walls removed without creating pools!\n")

    print("✅ Maze generation logic executed successfully!")

    # 3. Printing a sample of the final grid memory to confirm integer values
    print(f"\nSample data from Row 0: {maze.grid[0]}")
