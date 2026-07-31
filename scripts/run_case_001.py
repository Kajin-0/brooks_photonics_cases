#!/usr/bin/env python3
"""Execute Case 001 from downloaded WFC3/IR IMA products."""

from __future__ import annotations

import json
from pathlib import Path

from brooks_cases.plotting import plot_asymmetry, plot_interval_summary
from brooks_cases.wfc3 import load_ima, summarize_intervals

CASE_DIR = Path("cases/001_wfc3_ir_ramp_anomaly")
RAW_DIR = CASE_DIR / "data" / "raw"
DERIVED_DIR = CASE_DIR / "data" / "derived"
FIGURE_DIR = CASE_DIR / "figures"
EXPOSURES = {
    "scattered": "icqtbbbxq_ima.fits",
    "nominal": "icqtbbc0q_ima.fits",
}


def main() -> None:
    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    case_summary: dict[str, object] = {}

    for label, filename in EXPOSURES.items():
        path = RAW_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run `make download` first.")

        cube = load_ima(path)
        summary = summarize_intervals(cube)
        summary.to_csv(DERIVED_DIR / f"{label}_interval_summary.csv", index=False)
        plot_interval_summary(
            summary,
            FIGURE_DIR / f"{label}_interval_rates.png",
            f"WFC3/IR {label} exposure: interval rates",
        )
        plot_asymmetry(
            summary,
            FIGURE_DIR / f"{label}_left_right_asymmetry.png",
            f"WFC3/IR {label} exposure: spatial asymmetry",
        )

        case_summary[label] = {
            "filename": filename,
            "n_reads": int(cube.time_s.size),
            "n_intervals": int(summary.shape[0]),
            "flagged_intervals": summary.loc[summary["anomaly"], "interval_index"].astype(int).tolist(),
            "maximum_absolute_asymmetry": float(summary["left_right_asymmetry"].abs().max()),
            "median_interval_rate_e_s": float(summary["full_median_e_s"].median()),
        }

    (DERIVED_DIR / "case_summary.json").write_text(
        json.dumps(case_summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(case_summary, indent=2))


if __name__ == "__main__":
    main()
