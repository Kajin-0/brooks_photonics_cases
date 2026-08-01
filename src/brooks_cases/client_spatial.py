"""Decision-focused spatial figure for the Case 001 client report."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from brooks_cases.wfc3 import RampCube, instantaneous_rate, interval_good_mask

INK = "#172033"
MUTED = "#667085"
ORANGE = "#C35B2A"
PURPLE = "#6A3FA0"
RATE_UNIT = r"electrons s$^{-1}$ pixel$^{-1}$"
FONT_FAMILY = ["IBM Plex Sans", "DejaVu Sans"]


def _downsample_mean(array: np.ndarray, factor: int = 4) -> np.ndarray:
    height = array.shape[0] // factor * factor
    width = array.shape[1] // factor * factor
    trimmed = array[:height, :width]
    return np.nanmean(
        trimmed.reshape(height // factor, factor, width // factor, factor),
        axis=(1, 3),
    )


def plot_client_spatial_sequence(
    affected_cube: RampCube,
    control_cube: RampCube,
    output: Path,
    *,
    stages: tuple[tuple[int, str], ...] = (
        (0, "Strong spatial gradient"),
        (6, "Hidden common-mode tail"),
        (10, "Nominal late-ramp behavior"),
    ),
    border: int = 50,
) -> None:
    """Generate the six-panel client figure directly from the detector arrays."""
    plt.rcParams.update({"font.family": FONT_FAMILY})
    affected_rates, _ = instantaneous_rate(affected_cube)
    control_rates, _ = instantaneous_rate(control_cube)

    figure, axes = plt.subplots(len(stages), 2, figsize=(10.2, 8.0))
    figure.patch.set_facecolor("white")
    figure.subplots_adjust(
        left=0.185,
        right=0.965,
        top=0.925,
        bottom=0.045,
        hspace=0.24,
        wspace=0.18,
    )
    figure.text(
        0.39,
        0.965,
        "Affected exposure",
        ha="center",
        va="top",
        fontsize=12,
        fontweight=600,
        color=ORANGE,
    )
    figure.text(
        0.775,
        0.965,
        "Affected minus control",
        ha="center",
        va="top",
        fontsize=12,
        fontweight=600,
        color=PURPLE,
    )

    row_centers = np.linspace(0.795, 0.205, len(stages))
    for row, ((interval, stage_label), row_center) in enumerate(
        zip(stages, row_centers, strict=True)
    ):
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

        affected_display = _downsample_mean(affected)
        control_display = _downsample_mean(control)
        difference_display = _downsample_mean(difference)

        combined = np.concatenate(
            [
                affected_display[np.isfinite(affected_display)],
                control_display[np.isfinite(control_display)],
            ]
        )
        affected_low, affected_high = np.percentile(combined, [2, 98])
        difference_limit = np.percentile(
            np.abs(difference_display[np.isfinite(difference_display)]), 98
        )

        panels = (
            (
                affected_display,
                "viridis",
                float(affected_low),
                float(affected_high),
            ),
            (
                difference_display,
                "coolwarm",
                float(-difference_limit),
                float(difference_limit),
            ),
        )
        for column, (image, cmap, low, high) in enumerate(panels):
            axis = axes[row, column]
            rendered = axis.imshow(
                image,
                origin="lower",
                cmap=cmap,
                vmin=low,
                vmax=high,
                interpolation="nearest",
            )
            axis.set_xticks([])
            axis.set_yticks([])
            for spine in axis.spines.values():
                spine.set_color("#C7CED8")
                spine.set_linewidth(0.8)
            colorbar = figure.colorbar(
                rendered,
                ax=axis,
                fraction=0.044,
                pad=0.025,
            )
            colorbar.ax.tick_params(labelsize=7, colors=MUTED, length=2)
            colorbar.outline.set_linewidth(0.6)
            colorbar.outline.set_edgecolor("#AAB2BF")
            colorbar.set_label(RATE_UNIT, fontsize=7.1, color=MUTED, labelpad=5)

        figure.text(
            0.018,
            row_center,
            f"Interval {interval}\n{stage_label}",
            ha="left",
            va="center",
            fontsize=9.4,
            fontweight=600,
            color=INK,
            linespacing=1.25,
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        output,
        dpi=240,
        bbox_inches="tight",
        facecolor="white",
        pad_inches=0.08,
    )
    plt.close(figure)
