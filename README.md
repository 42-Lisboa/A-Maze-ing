*This project has been created as part of the 42 curriculum by jcosta-a.*

# 🧱 A-Maze-ing

<p align="left">
  <img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Validation-Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white" />
  <img src="https://img.shields.io/badge/Package_Manager-uv-DE5FE9?style=for-the-badge&logo=uv&logoColor=white" />
</p>

> A configurable maze generator written in Python. It reads a `KEY=VALUE` config file, digs a maze with an iterative **Depth-First Search**, stamps a closed **"42"** pattern in its centre, solves it with **Breadth-First Search**, writes it to a hexadecimal output file and shows it in an interactive, coloured terminal view. The generator is also shipped as a reusable, pip-installable package: **`mazegen`**.

---

## 📋 Summary

- [Description](#description)
- [Instructions](#instructions)
- [Project Structure](#project-structure)
- [Configuration File](#configuration-file)
- [Output File Format](#output-file-format)
- [Maze Generation Algorithm](#maze-generation-algorithm)
- [Reusable Module — `mazegen`](#reusable-module)
- [Key Techniques](#key-techniques)
- [General Rules](#general-rules)
- [Concepts Learned](#concepts-learned)
- [Resources](#resources)

---

<a name="description"></a>
<details open><summary><h2>📖 Description</h2></summary>

**A-Maze-ing** turns a small text config file into a random (or seed-reproducible) maze. The program runs as a four-stage pipeline, each stage owned by one class:

| Stage | Class | File | Role |
|-------|-------|------|------|
| ✅ | `MazeParser` | `a_maze_parser.py` | Reads the config file and validates every key with Pydantic |
| 🧱 | `MazeGenerator` | `a_maze_gen/a_maze_gen.py` | Builds a closed grid, reserves the "42" pattern and digs the paths with DFS |
| ▶️ | `MazeRunner` | `a_maze_ing.py` | Orchestrates the pipeline, solves the maze with BFS and exports it to a `.txt` file |
| 👾 | `MazeVisualizer` | `a_maze_vis.py` | Draws the maze in the terminal with ANSI colours and runs the interactive menu |

Two kinds of maze can be generated:

- **Perfect** (`PERFECT=True`) — exactly **one** path between any two cells, so exactly one way from the entry to the exit
- **Imperfect** (`PERFECT=False`) — dead-ends are opened to create loops and **multiple** paths, without ever creating a 3×3 open area


<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="instructions"></a>
<details open><summary><h2>⚙️ Instructions</h2></summary>

### Requirements

- Python **3.10+**
- [**uv**](https://docs.astral.sh/uv/) — installs the dependencies and runs the project
- Runtime dependency: `pydantic`
- Dev dependencies: `flake8`, `mypy`

### Install and run

```bash
make install     # uv sync: creates .venv and installs every dependency
make run         # uv run python a_maze_ing.py config.txt
```

Or run it directly with any config file:

```bash
UV_CACHE_DIR=.cache/uv uv run python a_maze_ing.py <config_file.txt>
```

### Makefile rules

Every `uv` command in the Makefile runs with `UV_CACHE_DIR=.cache/uv`, so uv's download cache stays inside the project folder (`.cache/uv`) instead of the home directory.

| Rule | Command | Description |
|------|---------|-------------|
| `make` / `make all` | `install` + `lint` + `lint-strict` + `build` | Installs the dependencies, runs both linters and builds the `mazegen` wheel |
| `make install` | `uv sync` | Creates `.venv` and installs runtime and dev dependencies |
| `make run` | `uv run python a_maze_ing.py config.txt` | Generates, solves, exports and displays the maze |
| `make debug` | `uv run python -m pdb a_maze_ing.py config.txt` | Runs the program inside the `pdb` debugger |
| `make clean` | `rm -rf .mypy_cache` + `__pycache__/` folders | Removes the mypy cache and the Python bytecode caches |
| `make fclean` | `clean` + `rm -rf maze.txt .venv .cache` | Also removes the generated maze, the virtual environment and the local uv cache |
| `make lint` | `flake8` + `mypy` (with the subject's flags) | Style and type checks |
| `make lint-strict` | `flake8` + `mypy --strict` | Stricter type checks |
| `make build` | `uv build` | Builds the `mazegen` wheel and moves it to the repository root |

### What happens when you run it

```
✅ Starting MazeParser...
 🔹 Configuration loaded successfully.
🧱 Starting MazeGenerator...
 🔹 Maze generated.
▶️  Starting MazeRunner...
 🔹 Maze successfully saved to 'maze.txt'.
👾 Starting MazeVisualizer...
```

After a 10-second pause, the interactive visualizer opens:

| Choice | Action |
|--------|--------|
| `1` | **Re-generate** a new maze with a new random seed (the output file is rewritten) |
| `2` | **Show / Hide** the shortest path from entry to exit |
| `3` | **Rotate** the wall colour: white → purple → turmaline → blue → rose → soft orange |
| `4` | **Break dead-ends**: makes the current maze imperfect and rewrites the output file |
| `5` | **Quit** |

| Element | Look in the terminal |
|---------|----------------------|
| Walls | `██` in the current palette colour |
| Entry | green `██` |
| Exit | red `██` |
| Shortest path | `🔸` |
| "42" pattern | green `██` cells framed by yellow `░░` |

### Error handling

| Situation | Behaviour |
|-----------|-----------|
| Wrong number of arguments | Prints the usage line and exits with status `1` |
| Config file cannot be opened | Prints the `OSError` and stops before generating anything |
| Invalid config value | Prints the Pydantic `ValidationError` with the reason, then stops |
| Output file cannot be written | Prints the `OSError` without crashing |

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="project-structure"></a>
<details open><summary><h2>📂 Project Structure</h2></summary>

| File(s) | Description |
|---------|-------------|
| `a_maze_ing.py` | Entry point. `MazeRunner` loads the config, generates the maze, solves it with BFS, exports it and starts the visualizer |
| `a_maze_parser.py` | `MazeParser` Pydantic model and `parse_config_file()`: reads `KEY=VALUE` lines and validates every value |
| `a_maze_gen/a_maze_gen.py` | `MazeGenerator`: closed grid, "42" pattern, DFS digger, dead-end breaker and 3×3 pool detection |
| `a_maze_gen/__init__.py` | Turns `a_maze_gen` into an importable package and exports `MazeGenerator` |
| `a_maze_vis.py` | `MazeVisualizer`: ANSI terminal rendering and the interactive menu |
| `config.txt` | Default configuration file |
| `ver_cores.py` | Small helper that prints the 256 ANSI terminal colours, used to pick the palette |
| `pyproject.toml` | Project metadata, dependencies and the `mazegen` package settings |
| `Makefile` | Install, run, debug, lint, clean, fclean and build rules |
| `LICENSE.md` | MIT License |

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="configuration-file"></a>
<details open><summary><h2>📝 Configuration File</h2></summary>

The config file is plain text with **one `KEY=VALUE` pair per line**:

- Lines starting with `#` are comments and are ignored
- Lines without `=` are ignored, so blank lines are fine
- Spaces around keys and values are trimmed

Default `config.txt`:

```ini
# 🔑 Main Keys
# --------------------------------------------------
WIDTH=20
HEIGHT=15
ENTRY=0,14
EXIT=19,0
OUTPUT_FILE=maze.txt
PERFECT=True

# ⭐ Additional Keys
# --------------------------------------------------
SEED=13
```

| Key | Required | Format | Rules | Default (`config.txt`) |
|-----|----------|--------|-------|------------------------|
| `WIDTH` | ✅ | integer | `9 ≤ WIDTH ≤ 50` | `20` |
| `HEIGHT` | ✅ | integer | `7 ≤ HEIGHT ≤ 50` | `15` |
| `ENTRY` | ✅ | `x,y` | Inside the grid, different from `EXIT`, not on the "42" pattern | `0,14` |
| `EXIT` | ✅ | `x,y` | Inside the grid, different from `ENTRY`, not on the "42" pattern | `19,0` |
| `OUTPUT_FILE` | ✅ | file name | Must end with `.txt`; spaces are removed | `maze.txt` |
| `PERFECT` | ❌ (falls back to `False`) | boolean | `True` → one single path; `False` → loops are added | `True` |
| `SEED` | ❌ (falls back to random) | integer | The same seed always gives the same maze | `13` |

Notes:

- Coordinates are `x,y`: `x` is the column (`0` = left) and `y` is the row (`0` = top). Spaces such as `0, 14` are accepted, negative values are rejected
- The minimum size of **9×7** guarantees that the 7×5 "42" pattern fits inside the maze with a border of free cells around it
- `PERFECT` accepts any boolean Pydantic understands: `True`/`False`, `true`/`false`, `1`/`0`, `yes`/`no`…

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="output-file-format"></a>
<details open><summary><h2>📤 Output File Format</h2></summary>

Each cell is written as **one hexadecimal digit**, one line per row. Every bit stores one wall: **`1` = closed**, **`0` = open**.

| Bit | Value | Binary | Wall |
|-----|-------|--------|------|
| 0 | `1` | `0001` | North |
| 1 | `2` | `0010` | East |
| 2 | `4` | `0100` | South |
| 3 | `8` | `1000` | West |

Examples: `f` (`1111`) is a fully closed cell, like every "42" cell; `d` (`1101`) has North, South and West closed and only East open.

After the grid and an empty line, the file holds the **entry**, the **exit** and the **shortest path** as a string of `N`, `E`, `S`, `W` moves. Output of the default `config.txt`:

```
d1155579551553d55553
96e9553a93a954555552
8556b96aac6a95397956
c3d52c56c53ea96c5453
9693c15153c56a95553a
c56c3afafafffaad396a
9517aafef857faa92aba
a9696afffafff86aea86
ae96d413fafd52d296c3
c54393eafafffc56ad52
93d46c5694793955293a
ac395553c396a853aaae
c3aab95696a96c3aeac3
96c68693e96c53ec547a
ed55456c56d554555556

0,14      # entry (x,y)
19,0       # exit  (x,y)
NENWNNESESSENNEEEESWWSWSEENESEENENNENESSWSEESEEEEEENNWNNWSSSWWNNWWNEEENNENNNENWWWWSSSWNNNNENWWSSWWNWWNNESENNEEESEEEEEEN
```

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="maze-generation-algorithm"></a>
<details open><summary><h2>🧠 Maze Generation Algorithm</h2></summary>

### Generation — iterative Depth-First Search (recursive backtracker)

1. **Closed grid** — `create_closed_cells()` fills every cell with `15` (`1111`): all four walls closed
2. **"42" pattern** — `get_42_coords()` centres a 7×5 pattern in the grid. Those cells are marked as *visited* before digging starts, so the digger never enters them and they stay fully closed (`f`)
3. **Dig** — `maze_digger()` starts at `ENTRY` with a stack:
   - look at the cell on top of the stack and shuffle the compass (`N`, `E`, `S`, `W`)
   - for the first unvisited neighbour inside the grid, remove the wall on **both** sides (`& ~wall`) and push the neighbour
   - if there is no unvisited neighbour left (`for ... else`), pop the cell and backtrack
4. **Imperfect mode** (`PERFECT=False`) — `break_extra_walls_de()` looks for dead-ends (cells with exactly 3 walls, `bit_count() == 3`) and removes one random wall towards a valid neighbour. If `has_3x3_pool()` finds a 3×3 open area, the wall is rebuilt and another one is tried

The DFS visits every free cell once and opens one wall per new cell, so the result is a **spanning tree**: every cell is reachable and there is exactly one path between any two cells, which is a perfect maze.

### Why DFS?

- **Perfect by construction** — no extra check is needed to guarantee a single path and full connectivity
- **Long, winding corridors** — DFS goes as deep as it can before backtracking, which gives harder, better-looking mazes than algorithms that produce many short dead-ends
- **Simple to make reproducible** — one `random.seed(SEED)` call before digging gives the same maze every time
- **Iterative, not recursive** — an explicit stack avoids Python's recursion limit (a 50×50 maze has 2,500 cells, while the default limit is 1,000 frames)
- **Pairs naturally with BFS** — the two graph traversals were studied together, and BFS is the right tool for the solver

### Solving — Breadth-First Search

`MazeRunner.solve_maze()` runs a BFS from `ENTRY`. The queue stores `(cell, path_so_far)` and the "42" cells are pre-marked as visited. BFS explores the maze layer by layer, so the first time it reaches `EXIT` it has found the **shortest** path, even in an imperfect maze with several routes.

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="reusable-module"></a>
<details open><summary><h2>♻️ Reusable Module — <code>mazegen</code></h2></summary>

The generator lives in its own package, `a_maze_gen`, so it can be reused in other projects. It is distributed as **`mazegen`** (see `pyproject.toml`).

| Item | Value |
|------|-------|
| Distribution name | `mazegen` |
| Version | `0.1.0` |
| Import name | `a_maze_gen` |
| Public class | `MazeGenerator` |
| Built file | `mazegen-0.1.0-py3-none-any.whl` |

### Build and install

```bash
make build                                      # creates mazegen-0.1.0-py3-none-any.whl at the repo root (also run by `make`)
pip install mazegen-0.1.0-py3-none-any.whl      # or: uv add ./mazegen-0.1.0-py3-none-any.whl
```

### Basic usage

```python
from a_maze_gen import MazeGenerator

maze = MazeGenerator(
    width=20,
    height=15,
    maze_entry=(0, 14),
    maze_exit=(19, 0),
    output_file="maze.txt",
    perfect=True,
    seed=42,            # same seed -> same maze; None -> random
)

maze.create_closed_cells()               # 1. every wall closed
maze.maze_digger(start=maze.maze_entry)  # 2. dig with DFS
if not maze.perfect:
    maze.break_extra_walls_de()          # 3. optional: add loops

print(maze.grid[0][0])          # bitmask of the top-left cell (N=1, E=2, S=4, W=8)
print(maze.get_42_coords())     # set of (x, y) cells used by the "42" pattern
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `width`, `height` | `int` | Grid size in cells |
| `maze_entry`, `maze_exit` | `tuple[int, int]` | `(x, y)` coordinates |
| `output_file` | `str` | Output file name, kept for the exporter |
| `perfect` | `bool` | `True` for a single path, `False` to add loops (default `False`) |
| `seed` | `int \| None` | Random seed for reproducible mazes (default `None`) |

| Method | Description |
|--------|-------------|
| `create_closed_cells()` | Fills `grid` with fully closed cells (`15`) |
| `maze_digger(start)` | Digs the paths with an iterative DFS from `start` |
| `break_extra_walls_de()` | Opens dead-ends to create loops, without making 3×3 pools |
| `has_3x3_pool()` | `True` if the grid contains a 3×3 open area |
| `get_42_coords()` | Returns the cells used by the "42" pattern |
| `grid` | The maze: `grid[y][x]` is the wall bitmask of a cell |

Notes:

- `MazeGenerator` does **not** validate its inputs; validate them first (e.g. with `MazeParser`)
- Use a **new instance** for every maze: `create_closed_cells()` appends rows to `grid`
- The BFS solver is `MazeRunner.solve_maze()` in `a_maze_ing.py`, outside the package

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="key-techniques"></a>
<details open><summary><h2>🛠 Key Techniques</h2></summary>

- **Bitmask walls** — `NORTH = 1 << 0` … `WEST = 1 << 3`; `cell & ~wall` opens a wall, `cell | wall` closes it again, `cell & wall` tests it (generator, runner, visualizer)
- **`int.bit_count()`** — counts the closed walls of a cell; `3` means a dead-end (generator)
- **Iterative DFS with a stack** — `stack[-1]` to peek, `append()` to go deeper, `pop()` to backtrack (generator)
- **`for ... else`** — the `else` block runs only when no neighbour triggered a `break`, which is exactly the backtrack case (generator)
- **Compass table** — `(dx, dy, wall_here, wall_there)` tuples remove the shared wall on both cells in a single loop (generator)
- **`random.seed()` + `random.shuffle()`** — random but reproducible digging order (generator)
- **BFS with a queue** — stores `(cell, path_trace)` pairs so the path is built while searching (runner)
- **Pydantic `BaseModel`** — `Field(ge=..., le=..., alias="WIDTH")` maps config keys to typed, bounded attributes (parser)
- **`@field_validator(mode="before")`** — turns the raw `"x,y"` string into a `tuple[int, int]` before type checking (parser)
- **`@model_validator(mode="after")`** — cross-field checks: bounds, entry ≠ exit, no overlap with the "42" pattern (parser)
- **`model_dump()`** — converts the validated model into a dict passed straight to `MazeGenerator(**data)` (runner)
- **`f"{cell:x}"`** — formats each cell as one hexadecimal digit for the output file (runner)
- **ANSI escape codes** — `\033[38;5;Nm` for 256 colours, `\033[0m` to reset, `\033[H\033[J` to clear the screen (visualizer)
- **Unicode Block Elements** — `█` (U+2588) for walls and `░` (U+2591) for the "42" frame, doubled to make square cells (visualizer)
- **2x+1 render matrix** — each cell takes one centre slot and shares wall slots with its neighbours (visualizer)
- **Packaging with `pyproject.toml`** — `[tool.setuptools] packages` + `uv build` produce the `mazegen` wheel; `__all__` defines the public API

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="general-rules"></a>
<details open><summary><h2>📐 General Rules</h2></summary>

- Python **3.10+** required
- Code must pass **`flake8`** and **`mypy`** (`--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`)
- Full **type hints** and **docstrings** on functions and classes
- Exceptions must be handled gracefully; the program must never crash unexpectedly
- A `Makefile` with `install`, `run`, `debug`, `clean` and `lint` rules (`lint-strict` optional)
- The program runs as `python3 a_maze_ing.py config.txt`, and a default config file must be in the repository
- The maze is random but **reproducible with a seed**; entry and exit must be different cells inside the maze
- Walls must be coherent: two neighbouring cells always agree on the wall between them
- Corridors can't be wider than 2 cells: **no 3×3 open area**
- The maze must show a **"42"** drawn with fully closed cells
- `PERFECT=True` means **exactly one path** between the entry and the exit
- The output file uses **one hexadecimal digit per cell**, followed by the entry, the exit and the shortest path
- The generation logic must be a **reusable module**, packaged as `mazegen-*` at the root of the repository

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="concepts-learned"></a>
<details open><summary><h2>📚 Concepts Learned</h2></summary>

- A maze is a **graph**: cells are nodes and open walls are edges, so graph algorithms can both build it and solve it
- **DFS vs BFS** — the same traversal with a different container: a **stack** (LIFO) goes deep and makes long corridors, a **queue** (FIFO) spreads out evenly and finds the shortest path
- Why a DFS maze is **perfect**: it builds a spanning tree, so there are no loops and every cell is reachable
- How to store **four booleans in one integer** with bitwise operators, and why hexadecimal is a natural way to write 4-bit values
- Turning **recursion into iteration** with an explicit stack to stay under Python's recursion limit
- Validating input at the edge of the program with **Pydantic**, so the rest of the code can trust its data
- Splitting a program into **single-responsibility classes** (parse → generate → solve/export → display)
- **Packaging** a module as a wheel so another project can `pip install` it
- Drawing in the terminal with **ANSI escape codes** and **Unicode block characters**
- Managing environments, dependencies and builds with **uv**

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<a name="resources"></a>
<details open><summary><h2>🔗 Resources</h2></summary>

| Title | Author | Description |
|-------|--------|-------------|
| [Como funciona os algoritmos DFS e BFS](https://www.youtube.com/watch?v=MtIKYXC-sn8&t=937s) | [Matheus Milanese](https://www.youtube.com/@matheusmilanese) | Visual explanation of how DFS and BFS traverse a graph, and how they differ. |
| [Depth-First Search in Python](https://www.datacamp.com/pt/tutorial/depth-first-search-in-python) | [DataCamp](https://www.datacamp.com) | DFS tutorial with Python code, both recursive and with an explicit stack — the base of the maze digger. |
| [Breadth-First Search in Python](https://www.datacamp.com/pt/tutorial/breadth-first-search-in-python) | [DataCamp](https://www.datacamp.com) | BFS tutorial with a queue and visited set — the base of the shortest-path solver. |
| [Block Elements — Unicode Explorer](https://unicode-explorer.com/b/2580) | [unicode-explorer.com](https://unicode-explorer.com) | Table of the Unicode Block Elements (`█`, `░`, `▀`…) used to draw walls and the "42" pattern. |
| [Python uv](https://www.datacamp.com/pt/tutorial/python-uv) | [DataCamp](https://www.datacamp.com) | Introduction to uv: projects, virtual environments, dependencies and running scripts. |
| [Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm) | [Wikipedia](https://en.wikipedia.org) | Overview of maze generation algorithms, including the randomized DFS / recursive backtracker. |
| [Validators — Pydantic Docs](https://docs.pydantic.dev/latest/concepts/validators/) | [Pydantic](https://docs.pydantic.dev) | Official reference for `field_validator` and `model_validator`, used to validate the config file. |
| [ANSI escape code](https://en.wikipedia.org/wiki/ANSI_escape_code) | [Wikipedia](https://en.wikipedia.org) | Reference for the colour and cursor codes used by the terminal visualizer. |

### 🤖 AI Usage

- This README was drafted with **Claude** (Anthropic) from the project's source code, config file and the resources above, then reviewed by the team

<p align="right"><a href="#-summary">⬆ back to summary</a></p>
</details>

---

<p align="left">
  Developed by <a href="https://github.com/jalvescodes">Jonathan Alves</a>
</p>
