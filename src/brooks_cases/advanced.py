"""Advanced robustness, source-mask, bootstrap, and FLT-comparison analyses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.ndimage import binary_dilation

from brooks_cases.comparison import compare_interval_summaries, comparison_metrics
from brooks_cases.wfc3 import (
    DATAREJECT_BIT,
    FltImage,
    RampCube,
    clipped_median,
    fit_ramp_slope,
    instantaneous_rate,
    interval_good_mask,
    normalized_left_right_asymmetry,
    robust_location_scale,
    trim_to_shape,
)


@dataclass(frozen=True)
class SourceMaskResult:
    """Source-free analysis mask and its diagnostic reference image."""

    analysis_mask: np.ndarray
    reference_rate_e_s: np.ndarray
    background_median_e_s: float
    background_scale_e_s: float
    retained_fraction: float


@dataclass(frozen=True)
class BootstrapResult:
    """Bootstrap interval table and report-level metric intervals."""

    interval_table: pd.DataFrame
    metrics: dict[str, float | int | list[int]]


def make_source_free_mask(
    control_cube: RampCube,
    *,
    late_interval_indices: Iterable[int] = range(9, 14),
    border: int = 50,
    source_sigma: float = 5.0,
    dilation_iterations: int = 3,
) -> SourceMaskResult:
    """Construct a source-free mask from late nominal-control interval rates.

    A median of late control interval maps suppresses isolated cosmic rays. Bright
    positive sources are detected relative to the robust background and dilated to
    exclude their wings. Reference pixels and detector edges are removed separately.
    """
    rates, _ = instantaneous_rate(control_cube)
    selected_maps: list[np.ndarray] = []
    for index in late_interval_indices:
        good = interval_good_mask(control_cube, int(index))
        selected_maps.append(np.where(good, rates[int(index)], np.nan))
    reference = np.nanmedian(np.stack(selected_maps), axis=0)

    interior = np.zeros(reference.shape, dtype=bool)
    interior[border:-border, border:-border] = True
    median, scale = robust_location_scale(reference[interior])
    if not np.isfinite(scale) or scale <= 0:
        raise RuntimeError("Could not estimate a finite source-detection scale")

    sources = reference > median + source_sigma * scale
    sources = binary_dilation(sources, iterations=dilation_iterations)
    analysis_mask = interior & np.isfinite(reference) & ~sources
    retained = float(analysis_mask.sum() / interior.sum())
    return SourceMaskResult(
        analysis_mask=analysis_mask,
        reference_rate_e_s=reference,
        background_median_e_s=median,
        background_scale_e_s=scale,
        retained_fraction=retained,
    )


def add_source_free_comparison(
    all_pixel_comparison: pd.DataFrame,
    test_source_free: pd.DataFrame,
    control_source_free: pd.DataFrame,
    *,
    late_intervals: int = 4,
    threshold_e_s: float = 0.05,
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Append source-free transient estimates to the baseline comparison table."""
    source_free = compare_interval_summaries(
        test_source_free,
        control_source_free,
        late_intervals=late_intervals,
        excess_threshold_e_s=threshold_e_s,
    )
    result = all_pixel_comparison.copy()
    result["source_free_test_median_e_s"] = source_free["test_full_median_e_s"]
    result["source_free_control_median_e_s"] = source_free["control_full_median_e_s"]
    result["source_free_transient_excess_e_s"] = source_free["transient_excess_e_s"]
    result["source_free_common_mode_flag"] = source_free["common_mode_flag"]
    result["source_free_minus_all_excess_e_s"] = (
        source_free["transient_excess_e_s"] - result["transient_excess_e_s"]
    )
    metrics = {
        "source_free_late_time_offset_e_s": float(source_free["late_time_offset_e_s"].iloc[0]),
        "source_free_integrated_excess_e_per_pixel": float(
            source_free["transient_excess_charge_e"].sum()
        ),
        "maximum_source_mask_effect_e_s": float(
            result["source_free_minus_all_excess_e_s"].abs().max()
        ),
        "median_source_mask_effect_e_s": float(
            result["source_free_minus_all_excess_e_s"].abs().median()
        ),
        "source_free_flag_agreement_fraction": float(
            np.mean(
                result["source_free_common_mode_flag"].to_numpy()
                == result["common_mode_flag"].to_numpy()
            )
        ),
    }
    return result, metrics


def threshold_sensitivity(
    test_summary: pd.DataFrame,
    control_summary: pd.DataFrame,
    *,
    thresholds_e_s: Iterable[float] = np.arange(0.02, 0.1001, 0.01),
    late_windows: Iterable[int] = range(3, 7),
) -> pd.DataFrame:
    """Sweep classification threshold and late-time baseline window."""
    rows: list[dict[str, object]] = []
    for late_intervals in late_windows:
        for threshold in thresholds_e_s:
            comparison = compare_interval_summaries(
                test_summary,
                control_summary,
                late_intervals=int(late_intervals),
                excess_threshold_e_s=float(threshold),
            )
            metrics = comparison_metrics(comparison)
            intervals = metrics["common_mode_flagged_intervals"]
            rows.append(
                {
                    "late_intervals": int(late_intervals),
                    "threshold_e_s": float(threshold),
                    "late_time_offset_e_s": metrics["late_time_offset_e_s"],
                    "flagged_count": len(intervals),
                    "last_flagged_interval": max(intervals) if intervals else -1,
                    "flagged_duration_s": metrics["common_mode_flagged_duration_s"],
                    "integrated_excess_e_per_pixel": metrics[
                        "integrated_transient_excess_e_per_pixel"
                    ],
                    "peak_excess_e_s": metrics["peak_transient_excess_e_s"],
                    "flagged_intervals": ",".join(str(value) for value in intervals),
                }
            )
    return pd.DataFrame(rows)


def _tile_difference_matrix(
    test_cube: RampCube,
    control_cube: RampCube,
    analysis_mask: np.ndarray,
    *,
    border: int = 50,
    tile_size: int = 32,
    minimum_valid_fraction: float = 0.60,
) -> tuple[np.ndarray, np.ndarray]:
    """Paired test-control tile medians for each interval."""
    test_rates, _ = instantaneous_rate(test_cube)
    control_rates, _ = instantaneous_rate(control_cube)
    if test_rates.shape != control_rates.shape:
        raise ValueError("Test and control rate cubes do not align")

    height, width = test_rates.shape[1:]
    test_good_masks = [
        interval_good_mask(test_cube, interval) for interval in range(test_rates.shape[0])
    ]
    control_good_masks = [
        interval_good_mask(control_cube, interval)
        for interval in range(control_rates.shape[0])
    ]
    tile_values: list[list[float]] = []
    tile_centers: list[tuple[float, float]] = []
    for y0 in range(border, height - border - tile_size + 1, tile_size):
        for x0 in range(border, width - border - tile_size + 1, tile_size):
            y1, x1 = y0 + tile_size, x0 + tile_size
            static = analysis_mask[y0:y1, x0:x1]
            if static.mean() < minimum_valid_fraction:
                continue
            interval_differences: list[float] = []
            for interval in range(test_rates.shape[0]):
                good = (
                    static
                    & test_good_masks[interval][y0:y1, x0:x1]
                    & control_good_masks[interval][y0:y1, x0:x1]
                )
                if good.mean() < minimum_valid_fraction:
                    interval_differences.append(np.nan)
                    continue
                test_median = clipped_median(test_rates[interval, y0:y1, x0:x1][good])
                control_median = clipped_median(control_rates[interval, y0:y1, x0:x1][good])
                interval_differences.append(test_median - control_median)
            tile_values.append(interval_differences)
            tile_centers.append((y0 + tile_size / 2, x0 + tile_size / 2))

    matrix = np.asarray(tile_values, dtype=np.float64).T
    centers = np.asarray(tile_centers, dtype=np.float64)
    usable = np.mean(np.isfinite(matrix), axis=0) >= 0.90
    matrix = matrix[:, usable]
    centers = centers[usable]
    if matrix.shape[1] < 50:
        raise RuntimeError("Too few valid spatial tiles for block bootstrap")
    return matrix, centers


def bootstrap_control_comparison(
    test_cube: RampCube,
    control_cube: RampCube,
    analysis_mask: np.ndarray,
    interval_durations_s: np.ndarray,
    *,
    late_intervals: int = 4,
    threshold_e_s: float = 0.05,
    tile_size: int = 32,
    n_bootstrap: int = 2000,
    seed: int = 14037,
) -> BootstrapResult:
    """Spatial block bootstrap for transient excess and integrated charge."""
    tile_matrix, _ = _tile_difference_matrix(
        test_cube,
        control_cube,
        analysis_mask,
        tile_size=tile_size,
    )
    rng = np.random.default_rng(seed)
    n_tiles = tile_matrix.shape[1]
    transient_samples = np.empty((n_bootstrap, tile_matrix.shape[0]), dtype=np.float64)
    offsets = np.empty(n_bootstrap, dtype=np.float64)
    charges = np.empty(n_bootstrap, dtype=np.float64)
    peak_excess = np.empty(n_bootstrap, dtype=np.float64)
    durations = np.empty(n_bootstrap, dtype=np.float64)

    for sample in range(n_bootstrap):
        indices = rng.integers(0, n_tiles, size=n_tiles)
        interval_difference = np.nanmedian(tile_matrix[:, indices], axis=1)
        offset = float(np.nanmedian(interval_difference[-late_intervals:]))
        transient = interval_difference - offset
        transient_samples[sample] = transient
        offsets[sample] = offset
        positive = np.clip(transient, 0.0, None)
        charges[sample] = float(np.sum(positive * interval_durations_s))
        peak_excess[sample] = float(np.max(transient))
        durations[sample] = float(
            np.sum(interval_durations_s[transient > threshold_e_s])
        )

    point_difference = np.nanmedian(tile_matrix, axis=1)
    point_offset = float(np.nanmedian(point_difference[-late_intervals:]))
    point_transient = point_difference - point_offset
    interval_table = pd.DataFrame(
        {
            "interval_index": np.arange(tile_matrix.shape[0], dtype=int),
            "point_transient_excess_e_s": point_transient,
            "ci95_low_e_s": np.percentile(transient_samples, 2.5, axis=0),
            "ci95_high_e_s": np.percentile(transient_samples, 97.5, axis=0),
            "probability_above_threshold": np.mean(
                transient_samples > threshold_e_s, axis=0
            ),
        }
    )
    metrics: dict[str, float | int | list[int]] = {
        "n_spatial_tiles": int(n_tiles),
        "n_bootstrap": int(n_bootstrap),
        "tile_size_pixels": int(tile_size),
        "late_time_offset_point_e_s": point_offset,
        "late_time_offset_ci95_low_e_s": float(np.percentile(offsets, 2.5)),
        "late_time_offset_ci95_high_e_s": float(np.percentile(offsets, 97.5)),
        "integrated_excess_point_e_per_pixel": float(
            np.sum(np.clip(point_transient, 0.0, None) * interval_durations_s)
        ),
        "integrated_excess_ci95_low_e_per_pixel": float(np.percentile(charges, 2.5)),
        "integrated_excess_ci95_high_e_per_pixel": float(np.percentile(charges, 97.5)),
        "peak_excess_ci95_low_e_s": float(np.percentile(peak_excess, 2.5)),
        "peak_excess_ci95_high_e_s": float(np.percentile(peak_excess, 97.5)),
        "flagged_duration_ci95_low_s": float(np.percentile(durations, 2.5)),
        "flagged_duration_ci95_high_s": float(np.percentile(durations, 97.5)),
        "high_confidence_flagged_intervals": interval_table.loc[
            interval_table["probability_above_threshold"] >= 0.95,
            "interval_index",
        ].astype(int).tolist(),
    }
    return BootstrapResult(interval_table=interval_table, metrics=metrics)


def _robust_map_residual(reference: np.ndarray, candidate: np.ndarray, mask: np.ndarray) -> dict[str, float]:
    valid = mask & np.isfinite(reference) & np.isfinite(candidate)
    residual = candidate[valid] - reference[valid]
    median, scale = robust_location_scale(residual)
    return {
        "median_residual_e_s": median,
        "residual_nmad_e_s": scale,
        "valid_pixel_fraction": float(valid.mean()),
    }


def flt_reconstruction_metrics(
    test_cube: RampCube,
    test_flt: FltImage,
    source_free_mask_ima: np.ndarray,
    *,
    clean_start_positive_read: int,
) -> tuple[dict[str, object], dict[str, np.ndarray]]:
    """Compare archived FLT with all-read and clean-read independent ramp slopes."""
    all_read_slope, all_read_n = fit_ramp_slope(test_cube, start_positive_read=0)
    clean_read_slope, clean_read_n = fit_ramp_slope(
        test_cube, start_positive_read=clean_start_positive_read
    )
    shape = test_flt.science_e_s.shape
    all_read = trim_to_shape(all_read_slope, shape)
    clean_read = trim_to_shape(clean_read_slope, shape)
    all_n = trim_to_shape(all_read_n, shape)
    clean_n = trim_to_shape(clean_read_n, shape)
    source_free = trim_to_shape(source_free_mask_ima, shape)
    flt_good = (test_flt.dq == 0) & np.isfinite(test_flt.science_e_s)
    mask = source_free & flt_good & np.isfinite(all_read) & np.isfinite(clean_read)

    all_residual = _robust_map_residual(test_flt.science_e_s, all_read, mask)
    clean_residual = _robust_map_residual(test_flt.science_e_s, clean_read, mask)
    metrics: dict[str, object] = {
        "flt_filename": test_flt.filename,
        "flt_bunit": test_flt.bunit,
        "clean_start_positive_read": int(clean_start_positive_read),
        "clean_start_time_s": float(
            test_cube.time_s[test_cube.time_s > 0][clean_start_positive_read]
        ),
        "archived_flt_source_free_median_e_s": clipped_median(
            test_flt.science_e_s[mask]
        ),
        "all_read_fit_source_free_median_e_s": clipped_median(all_read[mask]),
        "clean_read_fit_source_free_median_e_s": clipped_median(clean_read[mask]),
        "archived_flt_left_right_asymmetry": normalized_left_right_asymmetry(
            test_flt.science_e_s, mask
        ),
        "all_read_fit_left_right_asymmetry": normalized_left_right_asymmetry(all_read, mask),
        "clean_read_fit_left_right_asymmetry": normalized_left_right_asymmetry(
            clean_read, mask
        ),
        "all_read_vs_flt": all_residual,
        "clean_read_vs_flt": clean_residual,
        "median_valid_reads_all_fit": float(np.nanmedian(all_n[mask])),
        "median_valid_reads_clean_fit": float(np.nanmedian(clean_n[mask])),
        "ima_datareject_any_fraction": float(
            np.mean(np.any((test_cube.dq & DATAREJECT_BIT) != 0, axis=0))
        ),
    }
    maps = {
        "archived_flt": test_flt.science_e_s,
        "all_read_fit": all_read,
        "clean_read_fit": clean_read,
        "clean_minus_flt": clean_read - test_flt.science_e_s,
        "analysis_mask": mask,
    }
    return metrics, maps
