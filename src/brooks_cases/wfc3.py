"""WFC3/IR MULTIACCUM loading and detector-ramp diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.stats import sigma_clip


@dataclass(frozen=True)
class RampCube:
    """Calibrated WFC3/IR nondestructive reads sorted by increasing sample time."""

    rate_e_s: np.ndarray
    error_e_s: np.ndarray
    dq: np.ndarray
    time_s: np.ndarray
    sampnum: np.ndarray
    filename: str

    @property
    def counts_e(self) -> np.ndarray:
        return self.rate_e_s * self.time_s[:, None, None]


def load_ima(path: str | Path) -> RampCube:
    """Load a WFC3/IR IMA file and sort reads into chronological order.

    WFC3 IMA extensions are stored in reverse chronological order. The SCI arrays
    are calibrated count rates; multiplying by SAMPTIME recovers cumulative charge.
    """
    path = Path(path)
    rates: list[np.ndarray] = []
    errors: list[np.ndarray] = []
    dqs: list[np.ndarray] = []
    times: list[float] = []
    sampnums: list[int] = []

    with fits.open(path, memmap=True) as hdul:
        science_versions = sorted(
            int(hdu.header.get("EXTVER", 1)) for hdu in hdul if hdu.name == "SCI"
        )
        for version in science_versions:
            science_hdu = hdul["SCI", version]
            rates.append(np.array(science_hdu.data, dtype=np.float64, copy=True))
            errors.append(np.array(hdul["ERR", version].data, dtype=np.float64, copy=True))
            dqs.append(np.array(hdul["DQ", version].data, dtype=np.int32, copy=True))
            times.append(float(science_hdu.header.get("SAMPTIME", np.nan)))
            sampnums.append(int(science_hdu.header.get("SAMPNUM", -1)))

    time_array = np.asarray(times)
    if not np.all(np.isfinite(time_array)):
        raise ValueError(f"One or more SCI extensions lack finite SAMPTIME values: {path}")

    order = np.argsort(time_array)
    return RampCube(
        rate_e_s=np.stack(rates)[order],
        error_e_s=np.stack(errors)[order],
        dq=np.stack(dqs)[order],
        time_s=time_array[order],
        sampnum=np.asarray(sampnums)[order],
        filename=path.name,
    )


def instantaneous_rate(cube: RampCube) -> tuple[np.ndarray, np.ndarray]:
    """Return interval count rates and interval mid-times.

    For cumulative charge Q_i = R_i t_i, the interval rate is
    (Q_i - Q_{i-1}) / (t_i - t_{i-1}).
    """
    valid = cube.time_s > 0
    counts = cube.counts_e[valid]
    times = cube.time_s[valid]
    if times.size < 2:
        raise ValueError("At least two positive-time reads are required")
    delta_t = np.diff(times)
    if np.any(delta_t <= 0):
        raise ValueError("Sample times must be strictly increasing")
    rates = np.diff(counts, axis=0) / delta_t[:, None, None]
    return rates, 0.5 * (times[1:] + times[:-1])


def _clipped_median(values: np.ndarray, sigma: float = 4.0) -> float:
    finite = np.asarray(values, dtype=np.float64)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return float("nan")
    clipped = sigma_clip(finite, sigma=sigma, maxiters=5, masked=True)
    return float(np.ma.median(clipped))


def _robust_z(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    median = np.nanmedian(values)
    mad = np.nanmedian(np.abs(values - median))
    scale = 1.4826 * mad
    if not np.isfinite(scale) or scale == 0:
        return np.zeros_like(values)
    return (values - median) / scale


def summarize_intervals(
    cube: RampCube,
    *,
    border: int = 50,
    asymmetry_threshold: float = 0.10,
    z_threshold: float = 4.0,
) -> pd.DataFrame:
    """Summarize full-frame and left/right interval-rate behavior.

    The border removes reference/edge regions. Pixels carrying nonzero DQ values in
    either bounding read are excluded. An anomaly is flagged when either the robust
    full-frame rate score or normalized left/right asymmetry exceeds its threshold.
    """
    interval_rates, mid_times = instantaneous_rate(cube)
    positive_indices = np.flatnonzero(cube.time_s > 0)
    y_slice = slice(border, cube.rate_e_s.shape[1] - border)
    x0, x1 = border, cube.rate_e_s.shape[2] - border
    x_mid = (x0 + x1) // 2

    rows: list[dict[str, float | int | bool]] = []
    for interval_index, rate_map in enumerate(interval_rates):
        lower_read = positive_indices[interval_index]
        upper_read = positive_indices[interval_index + 1]
        good = (cube.dq[lower_read] == 0) & (cube.dq[upper_read] == 0)

        full_values = rate_map[y_slice, x0:x1]
        full_good = good[y_slice, x0:x1]
        left_values = rate_map[y_slice, x0:x_mid]
        left_good = good[y_slice, x0:x_mid]
        right_values = rate_map[y_slice, x_mid:x1]
        right_good = good[y_slice, x_mid:x1]

        full_median = _clipped_median(full_values[full_good])
        left_median = _clipped_median(left_values[left_good])
        right_median = _clipped_median(right_values[right_good])
        denominator = 0.5 * (abs(left_median) + abs(right_median))
        asymmetry = (left_median - right_median) / denominator if denominator > 0 else np.nan

        rows.append(
            {
                "interval_index": interval_index,
                "mid_time_s": float(mid_times[interval_index]),
                "full_median_e_s": full_median,
                "left_median_e_s": left_median,
                "right_median_e_s": right_median,
                "left_right_asymmetry": asymmetry,
                "good_pixel_fraction": float(np.mean(full_good)),
            }
        )

    frame = pd.DataFrame(rows)
    frame["full_rate_robust_z"] = _robust_z(frame["full_median_e_s"].to_numpy())
    frame["asymmetry_robust_z"] = _robust_z(frame["left_right_asymmetry"].to_numpy())
    frame["anomaly"] = (
        frame["left_right_asymmetry"].abs().gt(asymmetry_threshold)
        | frame["full_rate_robust_z"].abs().gt(z_threshold)
        | frame["asymmetry_robust_z"].abs().gt(z_threshold)
    )
    return frame


def pixel_ramp(cube: RampCube, y: int, x: int) -> pd.DataFrame:
    """Return one pixel's cumulative charge ramp and metadata."""
    return pd.DataFrame(
        {
            "time_s": cube.time_s,
            "sampnum": cube.sampnum,
            "rate_e_s": cube.rate_e_s[:, y, x],
            "counts_e": cube.counts_e[:, y, x],
            "error_e_s": cube.error_e_s[:, y, x],
            "dq": cube.dq[:, y, x],
        }
    )
