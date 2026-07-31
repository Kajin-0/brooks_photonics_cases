import numpy as np
import pandas as pd

from brooks_cases.advanced import make_source_free_mask, threshold_sensitivity
from brooks_cases.comparison import compare_interval_summaries, comparison_metrics
from brooks_cases.wfc3 import (
    DATAREJECT_BIT,
    RampCube,
    fit_ramp_slope,
    instantaneous_rate,
    interval_good_mask,
    summarize_intervals,
)


def make_cube() -> RampCube:
    time = np.array([0.0, 1.0, 3.0, 6.0])
    interval_rates = np.array([2.0, 2.0, 5.0])
    counts = np.zeros((4, 120, 120), dtype=float)
    for index, rate in enumerate(interval_rates, start=1):
        dt = time[index] - time[index - 1]
        counts[index] = counts[index - 1] + rate * dt
    rate = np.zeros_like(counts)
    rate[1:] = counts[1:] / time[1:, None, None]
    return RampCube(
        rate_e_s=rate,
        error_e_s=np.ones_like(rate),
        dq=np.zeros_like(rate, dtype=int),
        time_s=time,
        sampnum=np.arange(4),
        filename="synthetic_test_ima.fits",
    )


def test_instantaneous_rate_recovers_intervals() -> None:
    cube = make_cube()
    rates, mid_times = instantaneous_rate(cube)
    assert np.allclose(rates[:, 60, 60], [2.0, 5.0])
    assert np.allclose(mid_times, [2.0, 4.5])


def test_summary_has_expected_columns() -> None:
    summary = summarize_intervals(make_cube(), border=10)
    expected = {
        "full_median_e_s",
        "left_right_asymmetry",
        "anomaly",
        "datareject_fraction",
    }
    assert expected.issubset(summary.columns)
    assert len(summary) == 2


def test_datareject_is_diagnostic_not_permanent_mask() -> None:
    cube = make_cube()
    cube.dq[1, 60, 60] = DATAREJECT_BIT
    assert interval_good_mask(cube, 0)[60, 60]


def test_fit_ramp_slope_with_free_intercept_recovers_late_slope() -> None:
    time = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    counts = np.zeros((6, 40, 40), dtype=float)
    cumulative = np.array([0.0, 10.0, 12.0, 14.0, 16.0, 18.0])
    counts[:] = cumulative[:, None, None]
    rate = np.zeros_like(counts)
    rate[1:] = counts[1:] / time[1:, None, None]
    cube = RampCube(
        rate_e_s=rate,
        error_e_s=np.ones_like(rate),
        dq=np.zeros_like(rate, dtype=int),
        time_s=time,
        sampnum=np.arange(time.size),
        filename="late_slope.fits",
    )
    slope, n_reads = fit_ramp_slope(cube, start_positive_read=1)
    assert np.allclose(slope, 2.0)
    assert np.all(n_reads == 4)


def test_control_comparison_separates_static_offset_from_transient() -> None:
    test = pd.DataFrame(
        {
            "interval_index": [0, 1, 2, 3],
            "mid_time_s": [50.0, 150.0, 250.0, 350.0],
            "interval_duration_s": [100.0] * 4,
            "full_median_e_s": [1.4, 1.2, 1.0, 1.0],
            "left_right_asymmetry": [0.2, 0.1, 0.0, 0.0],
            "anomaly": [True, True, False, False],
        }
    )
    control = test.copy()
    control["full_median_e_s"] = [0.9, 0.9, 0.9, 0.9]
    control["left_right_asymmetry"] = 0.0
    control["anomaly"] = False
    comparison = compare_interval_summaries(
        test,
        control,
        late_intervals=2,
        excess_threshold_e_s=0.05,
    )
    metrics = comparison_metrics(comparison)
    assert np.isclose(comparison["late_time_offset_e_s"].iloc[0], 0.1)
    assert comparison["common_mode_flag"].tolist() == [True, True, False, False]
    assert np.isclose(metrics["integrated_transient_excess_e_per_pixel"], 60.0)


def test_threshold_sensitivity_records_endpoint() -> None:
    test = pd.DataFrame(
        {
            "interval_index": [0, 1, 2, 3],
            "mid_time_s": [50.0, 150.0, 250.0, 350.0],
            "interval_duration_s": [100.0] * 4,
            "full_median_e_s": [1.4, 1.2, 1.0, 1.0],
            "left_right_asymmetry": [0.2, 0.1, 0.0, 0.0],
            "anomaly": [True, True, False, False],
        }
    )
    control = test.copy()
    control["full_median_e_s"] = 0.9
    control["left_right_asymmetry"] = 0.0
    control["anomaly"] = False
    result = threshold_sensitivity(
        test,
        control,
        thresholds_e_s=[0.05],
        late_windows=[2],
    )
    assert result.loc[0, "last_flagged_interval"] == 1
    assert result.loc[0, "flagged_duration_s"] == 200.0


def test_source_mask_excludes_bright_source() -> None:
    cube = make_cube()
    rng = np.random.default_rng(14037)
    rates = cube.rate_e_s.copy() + rng.normal(0.0, 0.01, size=cube.rate_e_s.shape)
    rates[:, 55:65, 55:65] += 100.0
    control = RampCube(
        rate_e_s=rates,
        error_e_s=cube.error_e_s,
        dq=cube.dq,
        time_s=cube.time_s,
        sampnum=cube.sampnum,
        filename=cube.filename,
    )
    result = make_source_free_mask(
        control,
        late_interval_indices=[0, 1],
        border=10,
        source_sigma=3.0,
        dilation_iterations=1,
    )
    assert not result.analysis_mask[60, 60]
    assert result.analysis_mask[30, 30]
