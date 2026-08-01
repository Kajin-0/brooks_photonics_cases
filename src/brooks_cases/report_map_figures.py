"""Report-visible detector maps with consistent terminology and physical units."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from brooks_cases.wfc3 import RampCube, instantaneous_rate, interval_good_mask

RATE_UNIT = r"electrons s$^{-1}$ pixel$^{-1}$"
MUTED = "#667085"


def _downsample_mean(array: np.ndarray, factor: int = 4) -> np.ndarray:
    height = array.shape[0] // factor * factor
    width = array.shape[1] // factor * factor
    trimmed = array[:height, :width]
    return np.nanmean(
        trimmed.reshape(height // factor, factor, width // factor, factor),
        axis=(1, 3),
    )


def _style_colorbar(colorbar) -> None:  # type: ignore[no-untyped-def]
    colorbar.ax.tick_params(labelsize=7.2, colors=MUTED, length=2)
    colorbar.outline.set_linewidth(0.6)
    colorbar.outline.set_edgecolor("#AAB2BF")
    colorbar.set_label(RATE_UNIT, fontsize=7.2, color=MUTED, labelpad=5)


def plot_full_spatial_sequence(
    affected_cube: RampCube,
    control_cube: RampCube,
    output: Path,
    *,
    intervals: tuple[int, ...] = (0, 2, 6, 10),
    border: int = 50,
) -> None:
    """Plot the complete appendix sequence using affected/control terminology."""
    affected_rates, _ = instantaneous_rate(affected_cube)
    control_rates, _ = instantaneous_rate(control_cube)
    figure, axes = plt.subplots(len(intervals), 3, figsize=(13, 3.15 * len(intervals)))
    for row, interval in enumerate(intervals):
        good = interval_good_mask(affected_cube, interval) & interval_good_mask(
            control_cube, interval
        )
        affected = np.where(good, affected_rates[interval], np.nan)[
            border:-border, border:-border
        ]
        control = np.where(good, control_rates[interval], np.nan)[
            border:-border, border:-border
        ]
        difference = affected - control
        affected = _downsample_mean(affected)
        control = _downsample_mean(control)
        difference = _downsample_mean(difference)
        combined = np.concatenate(
            [affected[np.isfinite(affected)], control[np.isfinite(control)]]
        )
        vmin, vmax = np.percentile(combined, [2, 98])
        diff_limit = np.percentile(np.abs(difference[np.isfinite(difference)]), 98)
        panels = (
            (affected, "Affected exposure", "viridis", (vmin, vmax)),
            (control, "Nominal control", "viridis", (vmin, vmax)),
            (
                difference,
                "Affected minus control",
                "coolwarm",
                (-diff_limit, diff_limit),
            ),
        )
        for column, (image, title, cmap, limits) in enumerate(panels):
            axis = axes[row, column]
            rendered = axis.imshow(
                image,
                origin="lower",
                cmap=cmap,
                vmin=limits[0],
                vmax=limits[1],
                interpolation="nearest",
            )
            axis.set_title(f"Interval {interval}: {title}", fontsize=10.5)
            axis.set_xticks([])
            axis.set_yticks([])
            colorbar = figure.colorbar(rendered, ax=axis, fraction=0.045, pad=0.03)
            _style_colorbar(colorbar)
    figure.suptitle(
        "Representative WFC3/IR instantaneous interval-rate maps",
        fontsize=15,
        fontweight="bold",
    )
    figure.tight_layout(rect=(0, 0, 1, 0.98))
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=230, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def plot_flt_reconstruction_maps(maps: dict[str, np.ndarray], output: Path) -> None:
    """Plot archived and independently reconstructed products with units."""
    archived = maps["archived_flt"]
    all_read = maps["all_read_fit"]
    clean_read = maps["clean_read_fit"]
    residual = maps["clean_minus_flt"]
    mask = maps["analysis_mask"]
    valid_values = np.concatenate([archived[mask], all_read[mask], clean_read[mask]])
    vmin, vmax = np.percentile(valid_values[np.isfinite(valid_values)], [2, 98])
    residual_limit = np.percentile(np.abs(residual[mask]), 98)
    figure, axes = plt.subplots(2, 2, figsize=(10, 9))
    panels = (
        (archived, "Archived CALWF3 FLT", "viridis", vmin, vmax),
        (all_read, "Independent all-read slope", "viridis", vmin, vmax),
        (clean_read, "Independent post-transient slope", "viridis", vmin, vmax),
        (
            residual,
            "Post-transient slope minus archived FLT",
            "coolwarm",
            -residual_limit,
            residual_limit,
        ),
    )
    for axis, (image, title, cmap, low, high) in zip(axes.flat, panels, strict=True):
        display = _downsample_mean(np.where(mask, image, np.nan), factor=4)
        rendered = axis.imshow(
            display,
            origin="lower",
            cmap=cmap,
            vmin=low,
            vmax=high,
            interpolation="nearest",
        )
        axis.set_title(title, fontsize=10.5)
        axis.set_xticks([])
        axis.set_yticks([])
        colorbar = figure.colorbar(rendered, ax=axis, fraction=0.045, pad=0.03)
        _style_colorbar(colorbar)
    figure.suptitle(
        "Archived and independently reconstructed count-rate products",
        fontsize=15,
        fontweight="bold",
    )
    figure.tight_layout(rect=(0, 0, 1, 0.97))
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=230, bbox_inches="tight", facecolor="white")
    plt.close(figure)
