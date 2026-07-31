# Brooks Photonics Cases

Reproducible detector-characterization case studies built from public, traceable measurement data.

The objective is to demonstrate how Brooks Photonics converts raw or intermediate detector measurements into defensible engineering conclusions. Each case includes pinned provenance, download validation, detector-level analysis, quality controls, and a report outline.

## Case 001 — WFC3/IR HgCdTe ramp anomaly diagnosis

The first case uses real public Hubble WFC3/IR MULTIACCUM measurements. A strongly contaminated exposure is compared with a nominal exposure from the same visit. The analysis reconstructs interval charge rates from nondestructive reads, quantifies spatial asymmetry, and flags intervals that should not be accepted by a simple ramp fit.

See [`cases/001_wfc3_ir_ramp_anomaly`](cases/001_wfc3_ir_ramp_anomaly/README.md).

## Run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
make download
make analyze
```

Raw archive products are not committed. Exact MAST product URIs are pinned, and every local download is recorded with byte size and SHA-256 hash.
