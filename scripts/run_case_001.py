#!/usr/bin/env python3
"""Execute the complete Case 001 analysis from pinned WFC3/IR products."""

from __future__ import annotations

import json
from pathlib import Path

from brooks_cases.advanced import (
    add_source_free_comparison,
    bootstrap_control_comparison,
    flt_reconstruction_metrics,
    make_source_free_mask,
    threshold_sensitivity,
)
from brooks_cases.comparison import compare_interval_summaries, comparison_metrics
from brooks_cases.plotting import (
    plot_asymmetry,
    plot_bootstrap_uncertainty,
    plot_control_comparison,
    plot_datareject_fraction,
    plot_flt_reconstruction,
    plot_interval_summary,
    plot_representative_interval_maps,
    plot_source_free_validation,
    plot_threshold_sensitivity,
    plot_transient_excess,
)
from brooks_cases.reporting import build_case_001_report
from brooks_cases.wfc3 import load_flt, load_ima, summarize_intervals

CASE_DIR = Path("cases/001_wfc3_ir_ramp_anomaly")
RAW_DIR = CASE_DIR / "data" / "raw"
DERIVED_DIR = CASE_DIR / "data" / "derived"
FIGURE_DIR = CASE_DIR / "figures"
REPORT_DIR = CASE_DIR / "report"
EXPOSURES = {
    "scattered": "icqtbbbxq_ima.fits",
    "nominal": "icqtbbc0q_ima.fits",
}
FLT_FILES = {
    "scattered": "icqtbbbxq_flt.fits",
    "nominal": "icqtbbc0q_flt.fits",
}
THRESHOLD_E_S = 0.05
LATE_INTERVALS = 4


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    cubes = {}
    summaries = {}
    case_summary: dict[str, object] = {}
    for label, filename in EXPOSURES.items():
        path = RAW_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run `make download` first.")
        cube = load_ima(path)
        cubes[label] = cube
        summary = summarize_intervals(cube)
        summaries[label] = summary
        summary.to_csv(DERIVED_DIR / f"{label}_interval_summary.csv", index=False)
        plot_interval_summary(summary, FIGURE_DIR / f"{label}_interval_rates.png", f"WFC3/IR {label} exposure: interval rates")
        plot_asymmetry(summary, FIGURE_DIR / f"{label}_left_right_asymmetry.png", f"WFC3/IR {label} exposure: spatial asymmetry")
        case_summary[label] = {
            "filename": filename,
            "n_reads": int(cube.time_s.size),
            "n_intervals": int(summary.shape[0]),
            "flagged_intervals": summary.loc[summary["anomaly"], "interval_index"].astype(int).tolist(),
            "maximum_absolute_asymmetry": float(summary["left_right_asymmetry"].abs().max()),
            "median_interval_rate_e_s": float(summary["full_median_e_s"].median()),
            "peak_datareject_fraction": float(summary["datareject_fraction"].max()),
        }

    source_result = make_source_free_mask(cubes["nominal"])
    source_free_summaries = {
        label: summarize_intervals(cube, analysis_mask=source_result.analysis_mask)
        for label, cube in cubes.items()
    }
    for label, summary in source_free_summaries.items():
        summary.to_csv(DERIVED_DIR / f"{label}_source_free_interval_summary.csv", index=False)

    comparison = compare_interval_summaries(
        summaries["scattered"], summaries["nominal"],
        late_intervals=LATE_INTERVALS,
        excess_threshold_e_s=THRESHOLD_E_S,
    )
    comparison, source_metrics = add_source_free_comparison(
        comparison,
        source_free_summaries["scattered"],
        source_free_summaries["nominal"],
        late_intervals=LATE_INTERVALS,
        threshold_e_s=THRESHOLD_E_S,
    )
    comparison.to_csv(DERIVED_DIR / "exposure_comparison.csv", index=False)
    comparison_summary = comparison_metrics(comparison)
    case_summary["comparison"] = comparison_summary

    source_metrics.update({
        "retained_fraction": source_result.retained_fraction,
        "background_median_e_s": source_result.background_median_e_s,
        "background_scale_e_s": source_result.background_scale_e_s,
    })
    _write_json(DERIVED_DIR / "source_mask_metrics.json", source_metrics)

    sensitivity = threshold_sensitivity(summaries["scattered"], summaries["nominal"])
    sensitivity.to_csv(DERIVED_DIR / "threshold_sensitivity.csv", index=False)

    durations = summaries["scattered"]["interval_duration_s"].to_numpy(dtype=float)
    bootstrap = bootstrap_control_comparison(
        cubes["scattered"], cubes["nominal"], source_result.analysis_mask, durations,
        late_intervals=LATE_INTERVALS,
        threshold_e_s=THRESHOLD_E_S,
    )
    bootstrap.interval_table.to_csv(DERIVED_DIR / "bootstrap_interval_uncertainty.csv", index=False)
    _write_json(DERIVED_DIR / "bootstrap_metrics.json", bootstrap.metrics)

    scattered_flt_path = RAW_DIR / FLT_FILES["scattered"]
    if not scattered_flt_path.exists():
        raise FileNotFoundError(f"Missing required FLT product: {scattered_flt_path}")
    flt = load_flt(scattered_flt_path)
    common_mode_intervals = comparison_summary["common_mode_flagged_intervals"]
    clean_start_positive_read = max(common_mode_intervals) + 1 if common_mode_intervals else 0
    flt_metrics, flt_maps = flt_reconstruction_metrics(
        cubes["scattered"], flt, source_result.analysis_mask,
        clean_start_positive_read=clean_start_positive_read,
    )
    _write_json(DERIVED_DIR / "flt_reconstruction_metrics.json", flt_metrics)

    plot_control_comparison(comparison, FIGURE_DIR / "control_comparison.png")
    plot_transient_excess(comparison, FIGURE_DIR / "transient_excess.png", threshold_e_s=THRESHOLD_E_S)
    plot_source_free_validation(comparison, FIGURE_DIR / "source_free_validation.png")
    plot_threshold_sensitivity(sensitivity, FIGURE_DIR / "threshold_sensitivity.png")
    plot_bootstrap_uncertainty(comparison, bootstrap.interval_table, FIGURE_DIR / "bootstrap_uncertainty.png", threshold_e_s=THRESHOLD_E_S)
    plot_datareject_fraction(summaries["scattered"], summaries["nominal"], FIGURE_DIR / "datareject_fraction.png")
    plot_representative_interval_maps(cubes["scattered"], cubes["nominal"], FIGURE_DIR / "representative_interval_maps.png")
    plot_flt_reconstruction(flt_maps, FIGURE_DIR / "flt_reconstruction.png")

    case_summary["source_free"] = source_metrics
    case_summary["bootstrap"] = bootstrap.metrics
    case_summary["flt_reconstruction"] = flt_metrics
    case_summary["analysis_settings"] = {
        "common_mode_threshold_e_s": THRESHOLD_E_S,
        "late_intervals": LATE_INTERVALS,
        "source_sigma": 5.0,
        "source_dilation_pixels": 3,
        "bootstrap_tile_size_pixels": bootstrap.metrics["tile_size_pixels"],
        "bootstrap_replicates": bootstrap.metrics["n_bootstrap"],
    }
    _write_json(DERIVED_DIR / "case_summary.json", case_summary)

    report_path = REPORT_DIR / "Brooks_Photonics_Case_001.pdf"
    build_case_001_report(CASE_DIR, report_path)
    print(json.dumps(case_summary, indent=2))
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
