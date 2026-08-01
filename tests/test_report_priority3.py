from __future__ import annotations

import pandas as pd

from brooks_cases.report_charts import (
    plot_robustness_summary,
    plot_temporal_diagnosis,
)
from brooks_cases.report_priority2 import PRIORITY2_CSS
from brooks_cases.report_theme import REPORT_CSS


def _comparison_table() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "interval_index": list(range(8)),
            "mid_time_s": [50, 150, 250, 350, 450, 550, 650, 750],
            "test_full_median_e_s": [1.4, 1.28, 1.18, 1.10, 1.04, 1.00, 0.97, 0.95],
            "control_full_median_e_s": [0.88] * 8,
            "transient_excess_e_s": [0.50, 0.38, 0.28, 0.20, 0.13, 0.09, 0.06, 0.01],
            "common_mode_flag": [True, True, True, True, True, True, True, False],
        }
    )


def test_rectangular_report_geometry() -> None:
    combined_css = REPORT_CSS + PRIORITY2_CSS
    assert "border-radius:4px" not in combined_css
    assert "border-radius:999px" not in combined_css
    assert ".step:before" in REPORT_CSS
    assert "border-radius:50%" in REPORT_CSS


def test_priority3_charts_render(tmp_path) -> None:
    comparison = _comparison_table()
    temporal = tmp_path / "temporal.png"
    plot_temporal_diagnosis(comparison, temporal)
    assert temporal.exists()
    assert temporal.stat().st_size > 10_000

    sensitivity = pd.DataFrame(
        {
            "late_intervals": [3, 3, 4, 4, 5, 5, 6, 6],
            "threshold_e_s": [0.04, 0.05] * 4,
            "last_flagged_interval": [7, 6, 7, 6, 7, 6, 7, 6],
        }
    )
    bootstrap = pd.DataFrame(
        {
            "ci95_low_e_s": comparison["transient_excess_e_s"] - 0.01,
            "ci95_high_e_s": comparison["transient_excess_e_s"] + 0.01,
            "point_transient_excess_e_s": comparison["transient_excess_e_s"],
        }
    )
    robustness = tmp_path / "robustness.png"
    plot_robustness_summary(sensitivity, comparison, bootstrap, robustness)
    assert robustness.exists()
    assert robustness.stat().st_size > 10_000
