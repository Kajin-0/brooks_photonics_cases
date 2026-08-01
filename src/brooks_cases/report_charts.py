"""Editorial charts used by the public-facing Case 001 reports."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap

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
RATE_UNIT = r"electrons s$^{-1}$ pixel$^{-1}$"


def _set_defaults() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.labelsize": 10.5,
            "axes.edgecolor": "#AAB2BF",
            "axes.linewidth": 0.8,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelsize": 9.5,
            "ytick.labelsize": 9.5,
            "legend.fontsize": 9.2,
            "text.color": INK,
            "axes.labelcolor": INK,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def _clean(axis) -> None:  # type: ignore[no-untyped-def]
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.grid(axis="y", color=GRID, linewidth=0.7, alpha=0.8)
    axis.set_axisbelow(True)


def _save(figure, output: Path) -> None:  # type: ignore[no-untyped-def]
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=240, bbox_inches="tight", facecolor="white", pad_inches=0.08)
    plt.close(figure)


def plot_temporal_diagnosis(comparison: pd.DataFrame, output: Path) -> None:
    """Plot interval rate and matched-control transient excess as one narrative figure."""
    _set_defaults()
    figure, axes = plt.subplots(
        2,
        1,
        figsize=(10.5, 6.55),
        sharex=True,
        gridspec_kw={"height_ratios": [1.02, 0.98], "hspace": 0.12},
    )
    first_time = float(comparison["mid_time_s"].iloc[0])
    last_flagged = int(comparison.loc[comparison["common_mode_flag"], "interval_index"].max())
    last_time = float(
        comparison.loc[comparison["interval_index"] == last_flagged, "mid_time_s"].iloc[0]
    )

    axis = axes[0]
    axis.axvspan(first_time - 40, last_time + 40, color=PURPLE_LIGHT, alpha=0.62, linewidth=0)
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
    axis.text(
        (first_time + last_time) / 2,
        axis.get_ylim()[1] * 0.99,
        "Control-relative transient regime",
        color=PURPLE_DARK,
        fontsize=9.5,
        fontweight="bold",
        horizontalalignment="center",
        verticalalignment="top",
    )
    axis.set_ylabel(f"Median interval rate\n({RATE_UNIT})")
    axis.legend(frameon=False, loc="upper right", ncol=2)
    axis.set_title(
        "The ramp remains elevated after the strong spatial gradient fades",
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
    axis.set_ylabel(f"Control-relative excess\n({RATE_UNIT})")
    axis.set_xlabel("Interval midpoint (s)")
    _clean(axis)
    _save(figure, output)


def plot_robustness_summary(
    sensitivity: pd.DataFrame,
    comparison: pd.DataFrame,
    bootstrap: pd.DataFrame,
    output: Path,
) -> None:
    """Plot a decision heat map and spatial bootstrap uncertainty."""
    _set_defaults()
    figure, axes = plt.subplots(1, 2, figsize=(11.4, 4.9), gridspec_kw={"wspace": 0.36})

    axis = axes[0]
    pivot = sensitivity.pivot(
        index="late_intervals",
        columns="threshold_e_s",
        values="last_flagged_interval",
    ).sort_index().sort_index(axis=1)
    thresholds = pivot.columns.to_numpy(dtype=float)
    baselines = pivot.index.to_numpy(dtype=int)
    values = pivot.to_numpy(dtype=float)
    vmin = int(np.nanmin(values))
    vmax = int(np.nanmax(values))
    palette = ListedColormap(plt.cm.Purples(np.linspace(0.28, 0.92, vmax - vmin + 1)))
    norm = BoundaryNorm(np.arange(vmin - 0.5, vmax + 1.5), palette.N)
    image = axis.imshow(values, aspect="auto", cmap=palette, norm=norm, origin="lower")
    nominal_col = int(np.argmin(np.abs(thresholds - 0.05)))
    axis.axvline(nominal_col, color=ORANGE, linewidth=1.9)
    for row, _baseline in enumerate(baselines):
        axis.text(
            nominal_col,
            row,
            f"{int(values[row, nominal_col])}",
            ha="center",
            va="center",
            fontsize=9.3,
            fontweight="bold",
            color="white" if values[row, nominal_col] >= (vmin + vmax) / 2 else INK,
        )
    tick_positions = np.arange(0, len(thresholds), 2)
    axis.set_xticks(tick_positions)
    axis.set_xticklabels([f"{thresholds[index]:.2f}" for index in tick_positions])
    axis.set_yticks(np.arange(len(baselines)))
    axis.set_yticklabels([str(value) for value in baselines])
    axis.set_xlabel(f"Transient threshold ({RATE_UNIT})", fontsize=10.2)
    axis.set_ylabel("Late-baseline window (intervals)", fontsize=10.2)
    axis.set_title("Classification endpoint across decision settings", loc="left", fontsize=13.2)
    colorbar = figure.colorbar(image, ax=axis, fraction=0.047, pad=0.038)
    colorbar.set_label("Last flagged interval", fontsize=9.5)
    colorbar.set_ticks(range(vmin, vmax + 1))
    colorbar.ax.tick_params(labelsize=9.0)
    axis.text(
        nominal_col,
        len(baselines) - 0.58,
        "0.05 nominal",
        ha="center",
        va="top",
        color=ORANGE,
        fontsize=8.9,
        fontweight="bold",
    )
    axis.tick_params(labelsize=9.3)

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
        linewidth=2.5,
        marker="o",
        markersize=4.5,
        label="Tile-median estimate",
    )
    axis.axhline(
        0.05,
        color=ORANGE,
        linewidth=1.4,
        linestyle="--",
        label="Engineering threshold",
    )
    axis.axhline(0, color="#8992A3", linewidth=0.8)
    axis.set_title("Spatial bootstrap uncertainty", loc="left", fontsize=13.2)
    axis.set_xlabel("Interval midpoint (s)", fontsize=10.2)
    axis.set_ylabel(f"Transient excess ({RATE_UNIT})", fontsize=10.2)
    axis.legend(frameon=False, fontsize=9.2, loc="upper right")
    axis.tick_params(labelsize=9.3)
    _clean(axis)
    _save(figure, output)


def plot_spatial_and_dq(
    affected: pd.DataFrame,
    control: pd.DataFrame,
    output: Path,
) -> None:
    """Plot the evolution of spatial asymmetry and the pipeline rejection response."""
    _set_defaults()
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.45), gridspec_kw={"wspace": 0.28})
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
