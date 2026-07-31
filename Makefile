.PHONY: install download analyze test lint

install:
	python -m pip install -e ".[dev]"

download:
	python scripts/download_case_001.py

analyze:
	python scripts/run_case_001.py

test:
	pytest

lint:
	ruff check .
