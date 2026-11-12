MAIN_SCRIPT = a_maze_ing.py
CONFIG_FILE = config.txt
ARTIFACTS = .mypy_cache maze.txt uv.lock .venv
UV_RUN = uv run python
FLAGS = \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs


all: lint install

install:
		uv sync

run:
		$(UV_RUN) $(MAIN_SCRIPT) $(CONFIG_FILE)

debug:
		$(UV_RUN) -m pdb $(MAIN_SCRIPT) $(CONFIG_FILE)

clean:
		rm -rf $(ARTIFACTS)
		find . -name "__pycache__" -type d -prune -exec rm -rf {} +

lint:
		$(UV_RUN) -m flake8 *.py
		$(UV_RUN) -m mypy *.py $(FLAGS)

lint-strict:
		$(UV_RUN) -m flake8 *.py
		$(UV_RUN) -m mypy *.py --strict
