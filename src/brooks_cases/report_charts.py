"""Editorial charts used by the public-facing Case 001 report."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

INK = "#172033"
MUTED = "#667085"
GRID = "#D9DEE7"
PURPLE = "#6A3FA0"
PURPLE_DARK = "#4A286F"
PURPLE_LIGHT = "#E9DFF4"
ORANGE = "#C35B2A"
ORANGE_LIGHT = "#F7E4DB"
TEAL = "#157A7A"
BLUE = "#2D5F9A"


def _set_defaults() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "axes.edgecolor": "#AAB2BF",
            "axes.linewidth": 0.8,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "text.color": INK,
            "axes.labelcolor": INK,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def _clean(axis) -> None:  # type: ignore[no-untyped-def]
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.grid(axis="y", color=GRID, linewidth=0.7, alpha=0.8)
    axis.set_axisbelow(True)


def _save(figure, output: Path) -> None:  # type: ignore[no-untyped-def]
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def plot_temporal_diagnosis(comparison: pd.DataFrame, output: Path) -> None:
    """Plot interval rate and matched-control transient excess as one narrative figure."""
    _set_defaults()
    figure, axes = plt.subplots(
        2,
        1,
        figsize=(10.5, 6.8),
        sharex=True,
        gridspec_kw={"height_ratios": [1.05, 0.95], "hspace": 0.12},
    )
    axis = axes[0]
    axis.plot(
        comparison["mid_time_s"],
        comparison["test_full_median_e_s"],
        color=ORANGE,
        linewidth=2.5,
        marker="o",
        markersize=5,
        label="Affected exposure",
    )
    axis.plot(
        comparison["mid_time_s"],
        comparison["control_full_median_e_s"],
        color=TEAL,
        linewidth=2.2,
        marker="s",
        markersize=4.5,
        linestyle="--",
        label="Nominal control",
    )
    axis.axvspan(
        comparison["mid_time_s"].iloc[0] - 40,
        comparison["mid_time_s"].iloc[6] + 40,
        color=PURPLE_LIGHT,
        alpha=0.55,
        linewidth=0,
    )
    axis.annotate(
        "Common-mode transient regime",
        xy=(comparison["mid_time_s"].iloc[4], 1.08),
        xytext=(760, 1.27),
        arrowprops={"arrowstyle": "-", "color": PURPLE, "lw": 1.2},
        color=PURPLE_DARK,
        fontsize=10,
        fontweight="bold",
    )
    axis.set_ylabel("Median interval rate\n(e-/s/pixel)")
    axis.legend(frameon=False, loc="upper right", ncol=2)
    axis.set_title(
        "The affected ramp remains elevated after the obvious spatial gradient fades",
        loc="left",
        pad=12,
    )
    _clean(axis)

    axis = axes[1]
    axis.fill_between(
        comparison["mid_time_s"],
        0,
        comparison["transient_excess_e_s"],
        where=comparison["common_mode_flag"],
        color=ORANGE_LIGHT,
        alpha=0.95,
    )
    axis.plot(
        comparison["mid_time_s"],
        comparison["transient_excess_e_s"],
        color=PURPLE,
        linewidth=2.5,
        marker="o",
        markersize=5,
    )
    axis.axhline(0.05, color=ORANGE, linewidth=1.4, linestyle="--")
    axis.text(
        comparison["mid_time_s"].iloc[-1],
        0.055,
        "0.05 threshold",
        horizontalalignment="right",
        verticalalignment="bottom",
        color=ORANGE,
        fontsize=9,
        fontweight="bold",
    )
    axis.axhline(0, color="#8992A3", linewidth=0.8)
    axis.set_ylabel("Control-relative excess\n(e-/s/pixel)")
    axis.set_xlabel("Interval midpoint (s)")
    _clean(axis)
    _save(figure, output)


def plot_robustness_summary(
    sensitivity: pd.DataFrame,
    comparison: pd.DataFrame,
    bootstrap: pd.DataFrame,
    output: Path,
) -> None:
    """Plot decision-threshold sensitivity and spatial bootstrap uncertainty."""
    _set_defaults()
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"wspace": 0.28})
    colors = [PURPLE_DARK, PURPLE, BLUE, TEAL]
    markers = ["o", "s", "^", "D"]
    axis = axes[0]
    for (late_intervals, group), color, marker in zip(
        sensitivity.groupby("late_intervals"), colors, markers, strict=True
    ):
        axis.plot(
            group["threshold_e_s"],
            group["last_flagged_interval"],
            color=color,
            linewidth=2,
            marker=marker,
            markersize=4,
            label=f"{late_intervals}-interval baseline",
        )
    axis.axvline(0.05, color=ORANGE, linewidth=1.3, linestyle="--")
    axis.text(0.052, 8.15, "Nominal threshold", color=ORANGE, fontsize=8.5, va="top")
    axis.set_title("Threshold sensitivity", loc="left", fontsize=12.5)
    axis.set_xlabel("Transient threshold (e-/s/pixel)")
    axis.set_ylabel("Last flagged interval")
    axis.legend(frameon=False, fontsize=8, loc="lower left")
    _clean(axis)

    axis = axes[1]
    x_values = comparison["mid_time_s"].to_numpy()
    axis.fill_between(
        x_values,
        bootstrap["ci95_low_e_s"],
        bootstrap["ci95_high_e_s"],
        color=PURPLE_LIGHT,
        alpha=1,
        label="95% spatial bootstrap interval",
    )
    axis.plot(
        x_values,
        bootstrap["point_transient_excess_e_s"],
        color=PURPLE_DARK,
        linewidth=2.4,
        marker="o",
        markersize=4,
        label="Tile-median estimate",
    )
    axis.axhline(
        0.05,
        color=ORANGE,
        linewidth=1.3,
        linestyle="--",
        label="Engineering threshold",
    )
    axis.axhline(0, color="#8992A3", linewidth=0.8)
    axis.set_title("Spatial bootstrap interval", loc="left", fontsize=12.5)
    axis.set_xlabel("Interval midpoint (s)")
    axis.set_ylabel("Transient excess (e-/s/pixel)")
    axis.legend(frameon=False, fontsize=8, loc="upper right")
    _clean(axis)
    _save(figure, output)


def plot_spatial_and_dq(
    affected: pd.DataFrame,
    control: pd.DataFrame,
    output: Path,
) -> None:
    """Plot the evolution of spatial asymmetry and the pipeline rejection response."""
    _set_defaults()
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.5), gridspec_kw={"wspace": 0.28})
    axis = axes[0]
    axis.plot(
        affected["mid_time_s"],
        100 * affected["left_right_asymmetry"],
        color=ORANGE,
        linewidth=2.5,
        marker="o",
        markersize=4.5,
        label="Affected",
    )
    axis.plot(
        control["mid_time_s"],
        100 * control["left_right_asymmetry"],
        color=TEAL,
        linewidth=2.2,
        marker="s",
        markersize=4,
        linestyle="--",
        label="Control",
    )
    axis.axhline(0, color="#8992A3", linewidth=0.8)
    axis.axhline(10, color=PURPLE, linewidth=1, linestyle=":")
    axis.axhline(-10, color=PURPLE, linewidth=1, linestyle=":")
    axis.set_title("Spatial asymmetry", loc="left", fontsize=12.5)
    axis.set_xlabel("Interval midpoint (s)")
    axis.set_ylabel("Left-right asymmetry (%)")
    axis.legend(frameon=False)
    _clean(axis)

    axis = axes[1]
    axis.plot(
        affected["mid_time_s"],
        100 * affected["datareject_fraction"],
        color=ORANGE,
        linewidth=2.5,
        marker="o",
        markersize=4.5,
        label="Affected",
    )
    axis.plot(
        control["mid_time_s"],
        100 * control["datareject_fraction"],
        color=TEAL,
        linewidth=2.2,
        marker="s",
        markersize=4,
        linestyle="--",
        label="Control",
    )
    axis.set_title("Pipeline DATAREJECT fraction", loc="left", fontsize=12.5)
    axis.set_xlabel("Interval midpoint (s)")
    axis.set_ylabel("Pixels with DATAREJECT (%)")
    axis.legend(frameon=False)
    _clean(axis)
    _save(figure, output)
