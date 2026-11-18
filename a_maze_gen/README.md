# 🧱 mazegen — `a_maze_gen`

<p align="left">
  <img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Package-mazegen_0.1.0-DE5FE9?style=for-the-badge&logo=pypi&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" />
</p>

> The reusable maze generation module of [A-Maze-ing](../README.md). `MazeGenerator` builds a grid of bitmask cells, reserves a closed **"42"** pattern in its centre and digs the paths with an iterative **Depth-First Search**. Mazes can be **perfect** (one single path) or **imperfect** (with loops), and a **seed** makes them reproducible. It only uses the Python standard library.

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

A maze is built in three steps: close every cell, dig, and (optionally) add loops.

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

maze.create_closed_cells()               # 1. every wall closed
maze.maze_digger(start=maze.maze_entry)  # 2. dig the paths with DFS
if not maze.perfect:
    maze.break_extra_walls_de()          # 3. optional: open dead-ends

print(maze.grid[0][0])   # 11 → walls North, East and West closed
```

`maze.grid` is a list of rows: `maze.grid[y][x]` is the cell in column `x` and row `y`, with `(0, 0)` at the top-left.

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
| `width` | `int` | — | Number of columns |
| `height` | `int` | — | Number of rows |
| `maze_entry` | `tuple[int, int]` | — | `(x, y)` entry cell, also the usual DFS start |
| `maze_exit` | `tuple[int, int]` | — | `(x, y)` exit cell |
| `output_file` | `str` | — | Output file name, stored for the caller's exporter |
| `perfect` | `bool` | `False` | `True` for a single path, `False` when you plan to call `break_extra_walls_de()` |
| `seed` | `int \| None` | `None` | Random seed; the same seed gives the same maze |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `create_closed_cells()` | `list[list[int]]` | Fills `grid` with `height` rows of `width` cells set to `15` |
| `maze_digger(start)` | `None` | Seeds `random` (if `seed` is set) and digs the maze with an iterative DFS from `start` |
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
| `perfect` | `bool` | Perfect / imperfect flag |
| `seed` | `int \| None` | Seed used by `maze_digger()` |
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

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="examples"></a>
<details open><summary><h2>🧪 Examples</h2></summary>

All outputs below come from the [Quick Start](#quick-start) maze (15×9, seed `42`).

### Reproducible mazes

```python
def build(seed: int) -> list[list[int]]:
    maze = MazeGenerator(15, 9, (0, 0), (14, 8), "maze.txt", True, seed)
    maze.create_closed_cells()
    maze.maze_digger(start=maze.maze_entry)
    return maze.grid

print(build(7) == build(7))   # True
```

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

```
###############################
# #   #   #                 # #
# # ### # # ############# # # #
# #     #               # #   #
# ##### ### ### ######### ### #
#     # ### ### #######   #   #
##### # ### ### ####### ### ###
#     # ### ###     ###   #   #
# ##### ####### ####### # ### #
#   #   ####### ####### # # # #
### ### ####### ####### # # # #
# #   #   # ### ###     # #   #
# ### ### # ### ####### # #####
#   #   #   ### ####### #     #
# ##### # ################### #
#     # # #         #   #   # #
# # ### ### ####### # # # # # #
# #         #         #   #   #
###############################
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

Building the same maze with `perfect=False` runs `break_extra_walls_de()`, and the new loops open a shorter route:

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

<a name="license"></a>
<details open><summary><h2>📄 License</h2></summary>

Released under the [MIT License](../LICENSE.md).

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<p align="left">
  Developed by <a href="https://github.com/jalvescodes">Jonathan Alves</a>
</p>
