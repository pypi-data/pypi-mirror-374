install:
    uv sync --all-groups --all-extras

check: lint format-check type-check test

lint:
    uv run ruff check .

lint-fix:
    uv run ruff check --fix .

format-check:
    uv run ruff format --check --diff .

format:
    uv run ruff format .

type-check:
    uv run mypy src tests

test:
    uv run pytest -n auto .

build:
    uv build
