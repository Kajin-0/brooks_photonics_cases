"""Control-exposure comparison for detector-ramp case studies."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compare_interval_summaries(
    test: pd.DataFrame,
    control: pd.DataFrame,
    *,
    late_intervals: int = 4,
    excess_threshold_e_s: float = 0.05,
) -> pd.DataFrame:
    """Separate static exposure offset from time-variable common-mode excess.

    The late-time median difference is treated as a static exposure-to-exposure
    offset. The remaining positive difference is the transient excess. Spatial
    flags are retained separately because common-mode contamination can affect both
    detector halves while producing little left/right asymmetry.
    """
    if len(test) != len(control):
        raise ValueError("Test and control summaries must contain the same intervals")
    if late_intervals < 2 or late_intervals > len(test):
        raise ValueError("late_intervals must be between 2 and the number of intervals")
    if not np.allclose(test["mid_time_s"], control["mid_time_s"], rtol=0, atol=1e-3):
        raise ValueError("Test and control interval times do not align")

    comparison = pd.DataFrame(
        {
            "interval_index": test["interval_index"].astype(int),
            "mid_time_s": test["mid_time_s"].astype(float),
            "interval_duration_s": test["interval_duration_s"].astype(float),
            "test_full_median_e_s": test["full_median_e_s"].astype(float),
            "control_full_median_e_s": control["full_median_e_s"].astype(float),
            "test_left_right_asymmetry": test["left_right_asymmetry"].astype(float),
            "control_left_right_asymmetry": control["left_right_asymmetry"].astype(float),
        }
    )
    comparison["full_rate_difference_e_s"] = (
        comparison["test_full_median_e_s"] - comparison["control_full_median_e_s"]
    )
    late_offset = float(
        comparison["full_rate_difference_e_s"].tail(late_intervals).median()
    )
    comparison["late_time_offset_e_s"] = late_offset
    comparison["transient_excess_e_s"] = (
        comparison["full_rate_difference_e_s"] - late_offset
    )
    comparison["transient_excess_charge_e"] = (
        comparison["transient_excess_e_s"].clip(lower=0)
        * comparison["interval_duration_s"]
    )
    comparison["common_mode_flag"] = comparison["transient_excess_e_s"].gt(
        excess_threshold_e_s
    )
    comparison["spatial_flag"] = test["anomaly"].astype(bool).to_numpy()
    comparison["classification"] = np.select(
        [
            comparison["common_mode_flag"] & comparison["spatial_flag"],
            comparison["common_mode_flag"],
            comparison["spatial_flag"],
        ],
        ["common-mode + spatial", "common-mode", "spatial"],
        default="nominal",
    )
    return comparison


def comparison_metrics(comparison: pd.DataFrame) -> dict[str, object]:
    """Reduce a comparison table to report-ready engineering metrics."""
    control_charge = float(
        (
            comparison["control_full_median_e_s"]
            * comparison["interval_duration_s"]
        ).sum()
    )
    transient_charge = float(comparison["transient_excess_charge_e"].sum())
    common_mode = comparison.loc[comparison["common_mode_flag"], "interval_index"]
    spatial = comparison.loc[comparison["spatial_flag"], "interval_index"]
    return {
        "common_mode_flagged_intervals": common_mode.astype(int).tolist(),
        "spatial_flagged_intervals": spatial.astype(int).tolist(),
        "common_mode_flagged_duration_s": float(
            comparison.loc[comparison["common_mode_flag"], "interval_duration_s"].sum()
        ),
        "late_time_offset_e_s": float(comparison["late_time_offset_e_s"].iloc[0]),
        "peak_transient_excess_e_s": float(comparison["transient_excess_e_s"].max()),
        "integrated_transient_excess_e_per_pixel": transient_charge,
        "transient_excess_fraction_of_control_charge": (
            transient_charge / control_charge if control_charge > 0 else float("nan")
        ),
    }
