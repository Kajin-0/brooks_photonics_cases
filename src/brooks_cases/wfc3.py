"""WFC3/IR MULTIACCUM loading and detector-ramp diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.stats import sigma_clip

# Retain only DATAREJECT=8192 as diagnostic evidence. Every other standard
# 16-bit WFC3 DQ flag is rejected from the independent ramp analysis.
DATAREJECT_BIT = 8192
PERMANENT_REJECT_BITS = 0xFFFF & ~DATAREJECT_BIT


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


@dataclass(frozen=True)
class FltImage:
    """Single-ramp-fit WFC3/IR FLT science product."""

    science_e_s: np.ndarray
    error_e_s: np.ndarray
    dq: np.ndarray
    filename: str
    bunit: str


def load_ima(path: str | Path) -> RampCube:
    """Load a WFC3/IR IMA file and sort reads into chronological order."""
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


def load_flt(path: str | Path) -> FltImage:
    """Load the science, uncertainty, and DQ arrays from a WFC3/IR FLT product."""
    path = Path(path)
    with fits.open(path, memmap=True) as hdul:
        science_hdu = hdul["SCI", 1]
        return FltImage(
            science_e_s=np.array(science_hdu.data, dtype=np.float64, copy=True),
            error_e_s=np.array(hdul["ERR", 1].data, dtype=np.float64, copy=True),
            dq=np.array(hdul["DQ", 1].data, dtype=np.int32, copy=True),
            filename=path.name,
            bunit=str(science_hdu.header.get("BUNIT", "UNKNOWN")),
        )


def positive_read_indices(cube: RampCube) -> np.ndarray:
    """Indices of reads with nonzero integration time."""
    return np.flatnonzero(cube.time_s > 0)


def instantaneous_rate(cube: RampCube) -> tuple[np.ndarray, np.ndarray]:
    """Return consecutive positive-read interval rates and interval mid-times."""
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


def interval_good_mask(
    cube: RampCube,
    interval_index: int,
    *,
    reject_bits: int = PERMANENT_REJECT_BITS,
) -> np.ndarray:
    """Return pixels free of selected DQ bits in both reads bounding an interval."""
    positive = positive_read_indices(cube)
    if interval_index < 0 or interval_index >= positive.size - 1:
        raise IndexError("Interval index is outside the positive-read range")
    lower = cube.dq[positive[interval_index]]
    upper = cube.dq[positive[interval_index + 1]]
    return ((lower | upper) & reject_bits) == 0


def datareject_fraction(cube: RampCube, interval_index: int, *, border: int = 50) -> float:
    """Fraction of interior pixels carrying DATAREJECT in either bounding read."""
    positive = positive_read_indices(cube)
    lower = cube.dq[positive[interval_index]]
    upper = cube.dq[positive[interval_index + 1]]
    flagged = ((lower | upper) & DATAREJECT_BIT) != 0
    interior = flagged[border:-border, border:-border]
    return float(np.mean(interior))


def clipped_median(values: np.ndarray, sigma: float = 4.0) -> float:
    """Sigma-clipped median of finite values."""
    finite = np.asarray(values, dtype=np.float64)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return float("nan")
    clipped = sigma_clip(finite, sigma=sigma, maxiters=5, masked=True)
    return float(np.ma.median(clipped))


def robust_location_scale(values: np.ndarray) -> tuple[float, float]:
    """Return median and Gaussian-equivalent MAD scale."""
    finite = np.asarray(values, dtype=np.float64)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return float("nan"), float("nan")
    median = float(np.median(finite))
    scale = float(1.4826 * np.median(np.abs(finite - median)))
    return median, scale


def robust_z(values: np.ndarray) -> np.ndarray:
    """Median/MAD standardized scores."""
    median, scale = robust_location_scale(values)
    if not np.isfinite(scale) or scale == 0:
        return np.zeros_like(np.asarray(values, dtype=np.float64))
    return (np.asarray(values, dtype=np.float64) - median) / scale


def summarize_intervals(
    cube: RampCube,
    *,
    border: int = 50,
    asymmetry_threshold: float = 0.10,
    z_threshold: float = 4.0,
    analysis_mask: np.ndarray | None = None,
    reject_bits: int = PERMANENT_REJECT_BITS,
) -> pd.DataFrame:
    """Summarize full-frame and left/right interval-rate behavior."""
    interval_rates, mid_times = instantaneous_rate(cube)
    positive_times = cube.time_s[positive_read_indices(cube)]
    height, width = cube.rate_e_s.shape[1:]
    if analysis_mask is None:
        analysis_mask = np.ones((height, width), dtype=bool)
    if analysis_mask.shape != (height, width):
        raise ValueError("analysis_mask shape does not match the detector array")

    y_slice = slice(border, height - border)
    x0, x1 = border, width - border
    x_mid = (x0 + x1) // 2

    rows: list[dict[str, float | int | bool]] = []
    for interval_index, rate_map in enumerate(interval_rates):
        good = interval_good_mask(cube, interval_index, reject_bits=reject_bits)
        good &= analysis_mask

        full_values = rate_map[y_slice, x0:x1]
        full_good = good[y_slice, x0:x1]
        left_values = rate_map[y_slice, x0:x_mid]
        left_good = good[y_slice, x0:x_mid]
        right_values = rate_map[y_slice, x_mid:x1]
        right_good = good[y_slice, x_mid:x1]

        full_median = clipped_median(full_values[full_good])
        left_median = clipped_median(left_values[left_good])
        right_median = clipped_median(right_values[right_good])
        denominator = 0.5 * (abs(left_median) + abs(right_median))
        asymmetry = (left_median - right_median) / denominator if denominator > 0 else np.nan

        rows.append(
            {
                "interval_index": interval_index,
                "mid_time_s": float(mid_times[interval_index]),
                "interval_duration_s": float(
                    positive_times[interval_index + 1] - positive_times[interval_index]
                ),
                "full_median_e_s": full_median,
                "left_median_e_s": left_median,
                "right_median_e_s": right_median,
                "left_right_asymmetry": asymmetry,
                "good_pixel_fraction": float(np.mean(full_good)),
                "datareject_fraction": datareject_fraction(
                    cube, interval_index, border=border
                ),
            }
        )

    frame = pd.DataFrame(rows)
    frame["full_rate_robust_z"] = robust_z(frame["full_median_e_s"].to_numpy())
    frame["asymmetry_robust_z"] = robust_z(frame["left_right_asymmetry"].to_numpy())
    frame["anomaly"] = (
        frame["left_right_asymmetry"].abs().gt(asymmetry_threshold)
        | frame["full_rate_robust_z"].abs().gt(z_threshold)
        | frame["asymmetry_robust_z"].abs().gt(z_threshold)
    )
    return frame


def fit_ramp_slope(
    cube: RampCube,
    *,
    start_positive_read: int = 0,
    minimum_reads: int = 3,
    reject_bits: int = PERMANENT_REJECT_BITS,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit cumulative charge versus time with per-pixel DQ-aware OLS.

    The intercept is free, so a fit beginning after a transient estimates the later
    steady slope even though earlier excess charge remains accumulated in the ramp.
    """
    positive = positive_read_indices(cube)
    if start_positive_read < 0 or start_positive_read >= positive.size:
        raise ValueError("start_positive_read is outside the positive-read range")
    selected = positive[start_positive_read:]
    times = cube.time_s[selected, None, None]
    counts = cube.counts_e[selected]
    valid = np.isfinite(counts) & ((cube.dq[selected] & reject_bits) == 0)

    weights = valid.astype(np.float64)
    n = weights.sum(axis=0)
    sum_t = (weights * times).sum(axis=0)
    sum_q = np.where(valid, counts, 0.0).sum(axis=0)
    sum_tt = (weights * times * times).sum(axis=0)
    sum_tq = np.where(valid, times * counts, 0.0).sum(axis=0)
    denominator = n * sum_tt - sum_t * sum_t

    slope = np.full(n.shape, np.nan, dtype=np.float64)
    usable = (n >= minimum_reads) & (denominator > 0)
    slope[usable] = (
        n[usable] * sum_tq[usable] - sum_t[usable] * sum_q[usable]
    ) / denominator[usable]
    return slope, n


def trim_to_shape(array: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """Center-trim an array, primarily to remove IMA reference pixels for FLT comparison."""
    if array.shape == shape:
        return array
    dy = array.shape[0] - shape[0]
    dx = array.shape[1] - shape[1]
    if dy < 0 or dx < 0 or dy % 2 or dx % 2:
        raise ValueError(f"Cannot center-trim {array.shape} to {shape}")
    return array[dy // 2 : array.shape[0] - dy // 2, dx // 2 : array.shape[1] - dx // 2]


def normalized_left_right_asymmetry(
    image: np.ndarray,
    mask: np.ndarray,
    *,
    border: int = 45,
) -> float:
    """Normalized left-right median asymmetry for a 2-D science image."""
    height, width = image.shape
    x_mid = width // 2
    interior_y = slice(border, height - border)
    left = mask[interior_y, border:x_mid] & np.isfinite(image[interior_y, border:x_mid])
    right = mask[interior_y, x_mid : width - border] & np.isfinite(
        image[interior_y, x_mid : width - border]
    )
    left_median = clipped_median(image[interior_y, border:x_mid][left])
    right_median = clipped_median(image[interior_y, x_mid : width - border][right])
    denominator = 0.5 * (abs(left_median) + abs(right_median))
    return (left_median - right_median) / denominator if denominator > 0 else np.nan


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
