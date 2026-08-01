.PHONY: install download analyze report test lint all

install:
	python -m pip install -e ".[dev]"

download:
	python scripts/download_case_001.py

analyze:
	python scripts/run_case_001.py

report: analyze
	@echo "Report written to cases/001_wfc3_ir_ramp_anomaly/report/Brooks_Photonics_Case_001.pdf"

test:
	pytest

lint:
	ruff check .

all: lint test download analyze
