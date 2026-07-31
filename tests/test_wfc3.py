import numpy as np

from brooks_cases.wfc3 import RampCube, instantaneous_rate, summarize_intervals


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
    assert {"full_median_e_s", "left_right_asymmetry", "anomaly"}.issubset(summary.columns)
    assert len(summary) == 2
