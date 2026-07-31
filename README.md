# Brooks Photonics Cases

Reproducible detector-characterization case studies built from public, traceable measurement data.

The objective is to demonstrate how Brooks Photonics converts detector measurements into defensible engineering conclusions. Each completed case contains pinned provenance, validated downloads, analysis code, quality controls, uncertainty estimates, figures, derived data, and a portfolio-ready technical report.

## Case 001 — WFC3/IR HgCdTe ramp anomaly diagnosis

Case 001 uses four real public Hubble WFC3/IR products: two MULTIACCUM IMA ramps and their archived FLT count-rate products. An exposure affected by time-variable Earth-limb scattered light is compared with a nominal exposure from the same visit.

The analysis:

- reconstructs consecutive-read charge rates;
- separates spatial gradients from common-mode transient background;
- treats pipeline-generated `DATAREJECT` flags as diagnostic evidence rather than permanent detector defects;
- validates the result with a source-free mask;
- sweeps detection thresholds and late-ramp baseline windows;
- propagates spatial uncertainty with 779 detector tiles and 2,000 bootstrap resamples;
- independently reconstructs all-read and post-transient ramp slopes;
- compares the reconstructed products with the archived CALWF3 FLT image;
- generates a six-page Brooks Photonics technical report.

Principal result: intervals `0–3` contain strong spatial contamination, while a common-mode excess remains through interval `6`. The complete transient regime spans `700.002 s` at the stated `0.05 e-/s/pixel` engineering threshold. The result is most consistent with a time-variable external background, not an intrinsic HgCdTe detector defect.

See [`cases/001_wfc3_ir_ramp_anomaly`](cases/001_wfc3_ir_ramp_anomaly/README.md).

The finished report is generated at:

```text
cases/001_wfc3_ir_ramp_anomaly/report/Brooks_Photonics_Case_001.pdf
```

## Run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
make all
```

Raw archive products are not committed. Exact MAST product URIs are pinned, and each downloaded file is recorded with its byte size and SHA-256 digest.
