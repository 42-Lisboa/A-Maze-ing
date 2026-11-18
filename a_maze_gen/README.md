# 🧱 mazegen — `a_maze_gen`

<p align="left">
  <img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Package-mazegen_0.1.0-DE5FE9?style=for-the-badge&logo=pypi&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" />
</p>

> The reusable maze generation module of [A-Maze-ing](../README.md). `MazeGenerator` builds a grid of bitmask cells, reserves a closed **"42"** pattern in its centre and digs the paths with an iterative **Depth-First Search**. Mazes can be **perfect** (one single path) or **Pac-Man boards** (loops and almost no dead-ends), and a **seed** makes them reproducible. The generator code only uses the Python standard library.

---

## 📋 Summary

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Grid Encoding](#grid-encoding)
- [API Reference](#api-reference)
- [How It Works](#how-it-works)
- [Examples](#examples)
- [Notes & Limitations](#notes-limitations)
- [License](#license)

---

<a name="installation"></a>
<details open><summary><h2>📦 Installation</h2></summary>

The package is distributed as **`mazegen`** and imported as **`a_maze_gen`**.

| Item | Value |
|------|-------|
| Distribution name | `mazegen` |
| Version | `0.1.0` |
| Import name | `a_maze_gen` |
| Public API | `MazeGenerator` |
| Python | `>=3.10` |

Build the wheel from the root of the A-Maze-ing repository:

```bash
make build      # uv build → mazegen-0.1.0-py3-none-any.whl at the repo root
```

Or, without uv, in a fresh virtual environment:

```bash
python3 -m venv venv && . venv/bin/activate
pip install build
python -m build   # → dist/mazegen-0.1.0-py3-none-any.whl and dist/mazegen-0.1.0.tar.gz
```

Install it in another project:

```bash
pip install mazegen-0.1.0-py3-none-any.whl
# or
uv add ./mazegen-0.1.0-py3-none-any.whl
```

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="quick-start"></a>
<details open><summary><h2>🚀 Quick Start</h2></summary>

```python
from a_maze_gen import MazeGenerator

maze = MazeGenerator(
    width=15,
    height=9,
    maze_entry=(0, 0),
    maze_exit=(14, 8),
    output_file="maze.txt",
    perfect=True,
    seed=42,
)

grid = maze.generate()   # close every cell → dig with DFS → loops if perfect=False

print(grid[0][0])        # 11 → walls North, East and West closed
```

`maze.grid` (also returned by `generate()`) is a list of rows: `maze.grid[y][x]` is the cell in column `x` and row `y`, with `(0, 0)` at the top-left.

`generate()` runs three steps, which can also be called one by one on a **new** instance (with the same seed, this gives the same maze as `generate()`):

```python
maze = MazeGenerator(15, 9, (0, 0), (14, 8), "maze.txt", True, 42)
maze.create_closed_cells()               # 1. every wall closed
maze.maze_digger(start=maze.maze_entry)  # 2. dig the paths with DFS
if not maze.perfect:
    maze.break_extra_walls_de()          # 3. open dead-ends → loops
```

Invalid parameters raise a `ValueError` as soon as the object is created:

```python
try:
    MazeGenerator(width=5, height=5, maze_entry=(0, 0), maze_exit=(4, 4), output_file="maze.txt")
except ValueError as error:
    print(error)   # Size must be 9-50 (width) and 7-50 (height)
```

To get a solution (the shortest path from entry to exit), see [Solve it with BFS](#solve-it-with-bfs).

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="grid-encoding"></a>
<details open><summary><h2>🔢 Grid Encoding</h2></summary>

Every cell is an `int` from `0` to `15`. Each bit stores one wall: **`1` = closed**, **`0` = open**.

| Constant | Bit | Value | Binary | Wall |
|----------|-----|-------|--------|------|
| `NORTH` | 0 | `1` | `0001` | North |
| `EAST` | 1 | `2` | `0010` | East |
| `SOUTH` | 2 | `4` | `0100` | South |
| `WEST` | 3 | `8` | `1000` | West |

| Value | Hex | Meaning |
|-------|-----|---------|
| `15` | `f` | Fully closed cell (start state, and every "42" cell) |
| `11` | `b` | North, East and West closed → dead-end open to the South |
| `5` | `5` | North and South closed → horizontal corridor |
| `0` | `0` | No walls → crossroads |

The constants live in the inner module:

```python
from a_maze_gen.a_maze_gen import NORTH, EAST, SOUTH, WEST

cell = maze.grid[0][0]
is_east_open = not cell & EAST
```

Two neighbouring cells always agree on their shared wall: when the generator opens the East wall of a cell, it also opens the West wall of the cell on its right.

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="api-reference"></a>
<details open><summary><h2>📘 API Reference</h2></summary>

### `MazeGenerator(width, height, maze_entry, maze_exit, output_file, perfect=False, seed=None)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | `int` | — | Number of columns, `9` to `50` |
| `height` | `int` | — | Number of rows, `7` to `50` |
| `maze_entry` | `tuple[int, int]` | — | `(x, y)` entry cell, also the DFS start used by `generate()` |
| `maze_exit` | `tuple[int, int]` | — | `(x, y)` exit cell |
| `output_file` | `str` | — | Output file name, only stored for the caller's exporter (the package never writes files) |
| `perfect` | `bool` | `False` | `True` for a single path, `False` for a Pac-Man board with loops |
| `seed` | `int \| None` | `None` | Random seed; the same seed gives the same maze. `None` gives a random maze |

**Raises `ValueError`** if the size is out of range, the entry or exit is outside the grid or on a "42" cell, or the entry and exit are the same cell.

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `generate()` | `list[list[int]]` | Builds the whole maze: `create_closed_cells()`, `maze_digger(maze_entry)` and, if `perfect` is `False`, `break_extra_walls_de()`. Returns `grid` |
| `create_closed_cells()` | `list[list[int]]` | Resets `grid` to `height` rows of `width` cells set to `15` |
| `maze_digger(start)` | `None` | Digs the maze with an iterative DFS from `start`, shuffling the directions with the instance's seeded random generator |
| `break_extra_walls_de()` | `None` | Opens one wall of each dead-end where possible, without creating a 3×3 open area or touching the "42" |
| `has_3x3_pool()` | `bool` | `True` if the grid contains a 3×3 block with no inner walls |
| `get_42_coords()` | `set[tuple[int, int]]` | The `(x, y)` cells that form the centred "42" pattern |
| `is_neighbor_coords_valid(coords, visited)` | `bool` | `True` if `coords` is inside the grid and not in `visited` |

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `grid` | `list[list[int]]` | The maze, `grid[y][x]` |
| `width`, `height` | `int` | Grid size |
| `maze_entry`, `maze_exit` | `tuple[int, int]` | Entry and exit cells |
| `perfect` | `bool` | Perfect / Pac-Man board flag |
| `seed` | `int \| None` | Seed given to the constructor |
| `int_seed` | `random.Random` | Private random generator created from `seed`, used by `maze_digger()` and `break_extra_walls_de()` |
| `output_file` | `str` | Output file name |

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="how-it-works"></a>
<details open><summary><h2>🧠 How It Works</h2></summary>

### 1. Closed grid

`create_closed_cells()` starts with every wall closed (`15` in every cell).

### 2. The "42" pattern

`get_42_coords()` places a 7×5 pattern in the centre of the grid, starting at `((width - 7) // 2, (height - 5) // 2)`:

```
# . # . # # #
# . # . . . #
# # # . # # #
. . # . # . .
. . # . # # #
```

`#` cells are reserved. The digger and the dead-end breaker treat them as already visited, so they stay fully closed (`15`).

### 3. Digging — iterative DFS

`maze_digger(start)` uses a stack:

1. Look at the cell on top of the stack and shuffle the four directions
2. Take the first neighbour that is inside the grid and not visited yet, open the wall on **both** sides and push the neighbour
3. If no neighbour is left, pop the cell and backtrack

Every free cell is visited once and receives exactly one new opening, so the result is a **spanning tree**: all cells are connected and there is exactly one path between any two of them.

### 4. Loops — dead-end breaker

`break_extra_walls_de()` scans the grid for dead-ends (cells with 3 closed walls). For each one, it opens a random wall towards a neighbour that is inside the grid and not part of the "42". If that opening creates a 3×3 open area (`has_3x3_pool()`), the wall is closed again and the next wall is tried.

The tree is only ever opened up, so every cell stays reachable and each new opening closes a loop. The result is a Pac-Man board: open corners and centre, many independent loops, and no dead-ends except the 3 pockets inside the "42" glyph (see [Notes & Limitations](#notes-limitations)).

### 5. One call: `generate()`

`generate()` chains steps 1, 3 and, when `perfect` is `False`, step 4, starting the DFS at `maze_entry`. All random choices come from `int_seed`, a `random.Random(seed)` owned by the instance, so other code that uses the global `random` module cannot change the result.

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="examples"></a>
<details open><summary><h2>🧪 Examples</h2></summary>

All outputs below come from the [Quick Start](#quick-start) maze (15×9, seed `42`).

### Reproducible mazes

```python
def build(seed: int) -> list[list[int]]:
    return MazeGenerator(15, 9, (0, 0), (14, 8), "maze.txt", True, seed).generate()

print(build(7) == build(7))   # True
```

Use a **new instance** to rebuild a maze from its seed: calling `generate()` twice on the same object continues the same random sequence and gives a different maze.

### Draw it in ASCII

```python
from a_maze_gen.a_maze_gen import NORTH, EAST, SOUTH, WEST

def to_ascii(maze: MazeGenerator) -> str:
    blocked = maze.get_42_coords()
    rows = [["#"] * (maze.width * 2 + 1) for _ in range(maze.height * 2 + 1)]
    for y, line in enumerate(maze.grid):
        for x, cell in enumerate(line):
            if (x, y) in blocked:
                continue
            vx, vy = x * 2 + 1, y * 2 + 1
            rows[vy][vx] = " "
            if not cell & NORTH:
                rows[vy - 1][vx] = " "
            if not cell & EAST:
                rows[vy][vx + 1] = " "
            if not cell & SOUTH:
                rows[vy + 1][vx] = " "
            if not cell & WEST:
                rows[vy][vx - 1] = " "
    return "\n".join("".join(row) for row in rows)

print(to_ascii(maze))
```

### Solve it with BFS

The package generates mazes only. A shortest path takes a few lines of BFS over `grid`:

```python
from collections import deque

def solve(maze: MazeGenerator) -> str | None:
    moves = [(NORTH, 0, -1, "N"), (EAST, 1, 0, "E"),
             (SOUTH, 0, 1, "S"), (WEST, -1, 0, "W")]
    visited = {maze.maze_entry}
    queue = deque([(maze.maze_entry, "")])
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == maze.maze_exit:
            return path
        for wall, dx, dy, letter in moves:
            nxt = (x + dx, y + dy)
            if not maze.grid[y][x] & wall and nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, path + letter))
    return None

print(solve(maze))   # SSEESWWSESESESSEENEEEESENESENESE
```

### Perfect vs imperfect

Building the same maze with `perfect=False` makes `generate()` also run `break_extra_walls_de()`. Dead-ends drop from 18 to 3 (the "42" pockets), and the new loops open a shorter route:

| `perfect` | Shortest path | Moves |
|-----------|---------------|-------|
| `True` | `SSEESWWSESESESSEENEEEESENESENESE` | 32 |
| `False` | `EESESSSSESSSEEEEEENESENESE` | 26 |

### Export to hexadecimal

```python
print("\n".join("".join(f"{cell:x}" for cell in row) for row in maze.grid))
```

```
b9793955555513b
ac52c0515557ac2
c53afafafff9696
956afef857f83c3
c3d2fffafffaaba
bc3c3bfafd52ac6
87c386fefffec53
817ae955539393a
ec5456d5546c6c6
```

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="notes-limitations"></a>
<details open><summary><h2>⚠️ Notes & Limitations</h2></summary>

- **Size**: `9 ≤ width ≤ 50` and `7 ≤ height ≤ 50`. The minimum is what the 7×5 "42" needs with a free border around it, so the "42" is always present
- **"42" cells** are fully closed (`15`) and unreachable; the entry and the exit cannot be placed on them
- **Dead-ends in Pac-Man mode**: 3 dead-ends always remain, at offsets `(1, 1)`, `(5, 1)` and `(5, 3)` from the top-left corner of the "42". Pattern cells close them on three sides, so they cannot be opened
- **No solver inside the package**: it generates mazes only. Use a BFS over `grid`, as in [Solve it with BFS](#solve-it-with-bfs)
- **Reproducibility is per instance**: a second `generate()` call on the same object gives a different maze; create a new instance instead
- **No file output**: `output_file` is only stored, the caller writes the file (A-Maze-ing writes one hexadecimal digit per cell)
- **Dependencies**: the generator code only uses the standard library. The wheel currently also declares `pydantic`, because `pyproject.toml` is shared with the A-Maze-ing program

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="license"></a>
<details open><summary><h2>📄 License</h2></summary>

Released under the [MIT License](../LICENSE.md).

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<p align="left">
  Developed by <a href="https://github.com/jalvescodes">Jonathan Alves</a>
</p>
