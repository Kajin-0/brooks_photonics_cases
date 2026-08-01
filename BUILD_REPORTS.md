# Rebuilding Brooks Photonics Case 001 Reports

The reports are not authored in LaTeX. They are generated programmatically from:

- Python analysis code
- Matplotlib figures
- HTML page templates
- CSS typography and layout
- WeasyPrint PDF rendering

This source package contains the complete report generator, tests, pinned-data manifest, derived outputs, figures, and the validated Revision 1.7 PDFs. The original raw FITS products are not bundled; the download script retrieves and verifies them from MAST.

## Recommended environment

The reference build uses:

- Ubuntu 24.04 or WSL2
- Python 3.12
- IBM Plex fonts
- Liberation Sans for the Brooks Photonics running-header wordmark
- WeasyPrint 69 or the version resolved by `pyproject.toml`

Windows users should use WSL2 for the closest match to the validated GitHub Actions build.

## Ubuntu or WSL2 setup

```bash
sudo apt-get update
sudo apt-get install -y fonts-ibm-plex fonts-liberation python3.12 python3.12-venv

python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

If WeasyPrint reports missing system libraries, install its Ubuntu runtime dependencies:

```bash
sudo apt-get install -y \
  libcairo2 libpango-1.0-0 libpangoft2-1.0-0 \
  libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info
```

## Rebuild from the pinned public data

```bash
python scripts/download_case_001.py
REPORT_SOURCE_REF="$(git rev-parse HEAD 2>/dev/null || cat SOURCE_COMMIT.txt)" \
  python scripts/run_case_001.py
```

Equivalent Make targets are available:

```bash
make install
make download
REPORT_SOURCE_REF="$(git rev-parse HEAD 2>/dev/null || cat SOURCE_COMMIT.txt)" make analyze
```

## Generated reports

The build writes:

```text
cases/001_wfc3_ir_ramp_anomaly/report/Brooks_Photonics_Case_001.pdf
cases/001_wfc3_ir_ramp_anomaly/report/Brooks_Photonics_Case_001_Technical.pdf
```

The client report is six pages. The technical report is nine pages.

## Run validation

```bash
ruff check .
pytest
```

## Main report source files

```text
src/brooks_cases/reporting.py
src/brooks_cases/report_templates.py
src/brooks_cases/report_theme.py
src/brooks_cases/report_priority1.py
src/brooks_cases/report_priority2.py
src/brooks_cases/report_priority4.py
src/brooks_cases/report_charts.py
src/brooks_cases/report_map_figures.py
src/brooks_cases/client_spatial.py
```

- `report_templates.py` contains the page content and HTML structure.
- `report_theme.py` contains the baseline visual system.
- `report_priority4.py` contains the final IBM Plex typography, restored Brooks Photonics header wordmark, multicolor accents, hierarchy, and editorial replacements.
- `report_charts.py`, `report_map_figures.py`, and `client_spatial.py` generate report-specific figures.
- `report_priority2.py` controls revision metadata, the source URL, and QR generation.

## Reproducibility notes

- Source products are pinned in `cases/001_wfc3_ir_ramp_anomaly/data/manifest.csv`.
- Downloads are verified by byte count and SHA-256.
- Raw FITS files remain outside Git and are intentionally omitted from the source ZIP.
- `SOURCE_COMMIT.txt` records the exact source snapshot used to assemble the package.
- Set `REPORT_SOURCE_REF` to a Git commit or tag before building a publication copy so the embedded QR and source link remain immutable.
