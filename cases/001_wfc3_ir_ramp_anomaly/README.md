# Case 001 — WFC3/IR HgCdTe ramp anomaly diagnosis

## Engineering question

Can read-level detector diagnostics identify which intervals of a nondestructive HgCdTe ramp are contaminated, quantify the spatial signature, and show why a single fitted count-rate image is insufficient?

## Real data

This case uses two public WFC3/IR exposures from HST program 14037, visit BB:

- `icqtbbbxq_ima.fits`: strong time-variable Earth-limb scattered-light contamination in early reads;
- `icqtbbc0q_ima.fits`: nominal comparison exposure from the same visit.

The pair is used by the official STScI WFC3/IR IMA visualization tutorial. The repository pins the exact MAST product URIs in `data/manifest.csv`.

## Detector-level method

For each calibrated read, cumulative charge is reconstructed as

\[
Q_i(x,y)=R_i(x,y)t_i,
\]

and the interval rate is

\[
\dot Q_i(x,y)=\frac{Q_i(x,y)-Q_{i-1}(x,y)}{t_i-t_{i-1}}.
\]

The workflow then:

1. sorts IMA extensions into chronological order;
2. removes edge regions and pixels carrying nonzero data-quality flags;
3. computes sigma-clipped full-frame, left-half, and right-half interval medians;
4. quantifies normalized left-right asymmetry;
5. flags intervals using physical thresholds and robust z-scores;
6. compares the contaminated and nominal exposures.

## Reproduce

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install -e ".[dev]"
python scripts/download_case_001.py
python scripts/run_case_001.py
```

Raw FITS files are intentionally excluded from Git. The downloader writes an `inventory.json` containing exact SHA-256 hashes and byte sizes for the local copies.

## Expected outputs

```text
data/derived/scattered_interval_summary.csv
data/derived/nominal_interval_summary.csv
data/derived/case_summary.json
figures/scattered_interval_rates.png
figures/scattered_left_right_asymmetry.png
figures/nominal_interval_rates.png
figures/nominal_left_right_asymmetry.png
```

## Interpretation boundary

This first case diagnoses contamination in the measured detector ramps. It does not claim that the underlying HgCdTe material is defective. The analysis separates a read-dependent measurement condition from intrinsic detector behavior—precisely the distinction a credible characterization report must make.
