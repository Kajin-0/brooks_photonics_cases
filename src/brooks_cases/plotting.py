"""Plot generation for detector case-study outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from brooks_cases.wfc3 import RampCube, instantaneous_rate, interval_good_mask

PURPLE = "#5B2A86"
LIGHT_PURPLE = "#A88BC2"
DARK = "#171717"
GRAY = "#707070"


def _save(fig: plt.Figure, output: Path, *, svg: bool = True) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=200, bbox_inches="tight")
    if svg:
        fig.savefig(output.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


def plot_interval_summary(summary: pd.DataFrame, output: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(summary["mid_time_s"], summary["left_median_e_s"], marker="o", label="Left half", color=PURPLE)
    ax.plot(summary["mid_time_s"], summary["right_median_e_s"], marker="o", label="Right half", color=DARK)
    flagged = summary[summary["anomaly"]]
    ax.scatter(flagged["mid_time_s"], flagged["full_median_e_s"], marker="x", s=70, color=GRAY, label="Spatially flagged")
    ax.set_xlabel("Interval midpoint (s)")
    ax.set_ylabel("Sigma-clipped median interval rate (e-/s/pixel)")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    _save(fig, output)


def plot_asymmetry(summary: pd.DataFrame, output: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.axhline(0.0, linewidth=1, color=DARK)
    ax.plot(summary["mid_time_s"], summary["left_right_asymmetry"], marker="o", color=PURPLE)
    ax.set_xlabel("Interval midpoint (s)")
    ax.set_ylabel("Normalized left-right asymmetry")
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    _save(fig, output)


def plot_control_comparison(comparison: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(comparison["mid_time_s"], comparison["test_full_median_e_s"], marker="o", label="Contaminated exposure", color=PURPLE)
    ax.plot(comparison["mid_time_s"], comparison["control_full_median_e_s"], marker="o", label="Nominal control", color=DARK)
    ax.set_xlabel("Interval midpoint (s)")
    ax.set_ylabel("Full-frame median interval rate (e-/s/pixel)")
    ax.set_title("Measured interval rate: contaminated versus nominal exposure")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    _save(fig, output)


def plot_transient_excess(comparison: pd.DataFrame, output: Path, *, threshold_e_s: float = 0.05) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.axhline(0.0, linewidth=1, color=DARK)
    ax.axhline(threshold_e_s, linewidth=1, linestyle="--", color=GRAY, label="Engineering threshold")
    ax.plot(comparison["mid_time_s"], comparison["transient_excess_e_s"], marker="o", color=PURPLE, label="Transient excess above late-time offset")
    flagged = comparison[comparison["common_mode_flag"]]
    ax.scatter(flagged["mid_time_s"], flagged["transient_excess_e_s"], marker="x", s=70, color=DARK, label="Common-mode flagged")
    ax.set_xlabel("Interval midpoint (s)")
    ax.set_ylabel("Transient excess rate (e-/s/pixel)")
    ax.set_title("Time-variable excess relative to nominal control")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    _save(fig, output)


def plot_source_free_validation(comparison: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.axhline(0.0, linewidth=1, color=DARK)
    ax.plot(comparison["mid_time_s"], comparison["transient_excess_e_s"], marker="o", color=PURPLE, label="All accepted pixels")
    ax.plot(comparison["mid_time_s"], comparison["source_free_transient_excess_e_s"], marker="s", color=DARK, label="Source-free mask")
    ax.set_xlabel("Interval midpoint (s)")
    ax.set_ylabel("Transient excess rate (e-/s/pixel)")
    ax.set_title("Astrophysical-source masking sensitivity")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    _save(fig, output)


def plot_threshold_sensitivity(sensitivity: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    for late_intervals, group in sensitivity.groupby("late_intervals"):
        ax.plot(group["threshold_e_s"], group["last_flagged_interval"], marker="o", label=f"Late baseline: {late_intervals} intervals")
    ax.set_xlabel("Transient threshold (e-/s/pixel)")
    ax.set_ylabel("Last flagged interval")
    ax.set_title("Classification sensitivity to threshold and baseline window")
    ax.set_yticks(range(-1, int(sensitivity["last_flagged_interval"].max()) + 1))
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    _save(fig, output)


def plot_bootstrap_uncertainty(comparison: pd.DataFrame, bootstrap: pd.DataFrame, output: Path, *, threshold_e_s: float = 0.05) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    x = comparison["mid_time_s"].to_numpy()
    ax.fill_between(x, bootstrap["ci95_low_e_s"], bootstrap["ci95_high_e_s"], color=LIGHT_PURPLE, alpha=0.45, label="95% spatial block-bootstrap interval")
    ax.plot(x, bootstrap["point_transient_excess_e_s"], marker="o", color=PURPLE, label="Source-free tile-median estimate")
    ax.axhline(threshold_e_s, color=DARK, linestyle="--", label="Engineering threshold")
    ax.axhline(0.0, color=GRAY, linewidth=1)
    ax.set_xlabel("Interval midpoint (s)")
    ax.set_ylabel("Transient excess rate (e-/s/pixel)")
    ax.set_title("Spatial block-bootstrap uncertainty")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    _save(fig, output)


def plot_datareject_fraction(scattered_summary: pd.DataFrame, nominal_summary: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.7))
    ax.plot(scattered_summary["mid_time_s"], 100 * scattered_summary["datareject_fraction"], marker="o", color=PURPLE, label="Contaminated exposure")
    ax.plot(nominal_summary["mid_time_s"], 100 * nominal_summary["datareject_fraction"], marker="o", color=DARK, label="Nominal control")
    ax.set_xlabel("Interval midpoint (s)")
    ax.set_ylabel("Pixels with DATAREJECT in bounding reads (%)")
    ax.set_title("Pipeline up-the-ramp rejection response")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    _save(fig, output)


def _downsample_mean(array: np.ndarray, factor: int = 4) -> np.ndarray:
    height = array.shape[0] // factor * factor
    width = array.shape[1] // factor * factor
    trimmed = array[:height, :width]
    return np.nanmean(trimmed.reshape(height // factor, factor, width // factor, factor), axis=(1, 3))


def plot_representative_interval_maps(test_cube: RampCube, control_cube: RampCube, output: Path, *, intervals: tuple[int, ...] = (0, 2, 6, 10), border: int = 50) -> None:
    test_rates, _ = instantaneous_rate(test_cube)
    control_rates, _ = instantaneous_rate(control_cube)
    fig, axes = plt.subplots(len(intervals), 3, figsize=(13, 3.2 * len(intervals)))
    for row, interval in enumerate(intervals):
        good = interval_good_mask(test_cube, interval) & interval_good_mask(control_cube, interval)
        test = np.where(good, test_rates[interval], np.nan)[border:-border, border:-border]
        control = np.where(good, control_rates[interval], np.nan)[border:-border, border:-border]
        difference = test - control
        test = _downsample_mean(test)
        control = _downsample_mean(control)
        difference = _downsample_mean(difference)
        combined = np.concatenate([test[np.isfinite(test)], control[np.isfinite(control)]])
        vmin, vmax = np.percentile(combined, [2, 98])
        diff_limit = np.percentile(np.abs(difference[np.isfinite(difference)]), 98)
        panels = [
            (test, "Contaminated", "gray", (vmin, vmax)),
            (control, "Nominal control", "gray", (vmin, vmax)),
            (difference, "Test - control", "coolwarm", (-diff_limit, diff_limit)),
        ]
        for column, (image, title, cmap, limits) in enumerate(panels):
            axis = axes[row, column]
            im = axis.imshow(image, origin="lower", cmap=cmap, vmin=limits[0], vmax=limits[1])
            axis.set_title(f"Interval {interval}: {title}")
            axis.set_xticks([])
            axis.set_yticks([])
            fig.colorbar(im, ax=axis, fraction=0.045, pad=0.03)
    fig.suptitle("Representative WFC3/IR instantaneous interval-rate maps", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    _save(fig, output, svg=False)


def plot_flt_reconstruction(maps: dict[str, np.ndarray], output: Path) -> None:
    archived = maps["archived_flt"]
    all_read = maps["all_read_fit"]
    clean_read = maps["clean_read_fit"]
    residual = maps["clean_minus_flt"]
    mask = maps["analysis_mask"]
    valid_values = np.concatenate([archived[mask], all_read[mask], clean_read[mask]])
    vmin, vmax = np.percentile(valid_values[np.isfinite(valid_values)], [2, 98])
    residual_limit = np.percentile(np.abs(residual[mask]), 98)
    fig, axes = plt.subplots(2, 2, figsize=(10, 9))
    panels = [
        (archived, "Archived CALWF3 FLT", "gray", vmin, vmax),
        (all_read, "Independent all-read slope", "gray", vmin, vmax),
        (clean_read, "Independent post-transient slope", "gray", vmin, vmax),
        (residual, "Post-transient slope - archived FLT", "coolwarm", -residual_limit, residual_limit),
    ]
    for axis, (image, title, cmap, low, high) in zip(axes.flat, panels, strict=True):
        display = _downsample_mean(np.where(mask, image, np.nan), factor=4)
        im = axis.imshow(display, origin="lower", cmap=cmap, vmin=low, vmax=high)
        axis.set_title(title)
        axis.set_xticks([])
        axis.set_yticks([])
        fig.colorbar(im, ax=axis, fraction=0.045, pad=0.03)
    fig.suptitle("Archived and independently reconstructed count-rate products", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    _save(fig, output, svg=False)
