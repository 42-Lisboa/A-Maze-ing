MAIN_SCRIPT = a_maze_ing.py
CONFIG_FILE = config.txt
ARTIFACTS = maze.txt .venv .cache
UV_CACHE_PREFIX = UV_CACHE_DIR=.cache/uv
UV_RUN = $(UV_CACHE_PREFIX) uv run python
FLAGS = \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs


all: install lint lint-strict build

install:
		$(UV_CACHE_PREFIX) uv sync

run:
		$(UV_RUN) $(MAIN_SCRIPT) $(CONFIG_FILE)

debug:
		$(UV_RUN) -m pdb $(MAIN_SCRIPT) $(CONFIG_FILE)

clean:
		rm -rf .mypy_cache
		find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
		rm -rf $(ARTIFACTS)

lint:
		$(UV_RUN) -m flake8 *.py
		$(UV_RUN) -m mypy *.py $(FLAGS)

lint-strict:
		$(UV_RUN) -m flake8 *.py
		$(UV_RUN) -m mypy *.py --strict

build:
		$(UV_CACHE_PREFIX) uv build
		mv dist/*.whl .
		rm -rf dist/
		rm -rf *.egg-info/


.PHONY: install run debug clean fclean lint lint-strict build
