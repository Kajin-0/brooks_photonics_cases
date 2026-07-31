"""Plot generation for case-study outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_interval_summary(summary: pd.DataFrame, output: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(summary["mid_time_s"], summary["left_median_e_s"], marker="o", label="Left")
    ax.plot(summary["mid_time_s"], summary["right_median_e_s"], marker="o", label="Right")
    flagged = summary[summary["anomaly"]]
    ax.scatter(
        flagged["mid_time_s"],
        flagged["full_median_e_s"],
        marker="x",
        label="Spatially flagged",
    )
    ax.set_xlabel("Interval midpoint (s)")
    ax.set_ylabel("Sigma-clipped median interval rate (e-/s/pixel)")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_asymmetry(summary: pd.DataFrame, output: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.axhline(0.0, linewidth=1)
    ax.plot(summary["mid_time_s"], summary["left_right_asymmetry"], marker="o")
    ax.set_xlabel("Interval midpoint (s)")
    ax.set_ylabel("Normalized left-right asymmetry")
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_control_comparison(comparison: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(
        comparison["mid_time_s"],
        comparison["test_full_median_e_s"],
        marker="o",
        label="Contaminated exposure",
    )
    ax.plot(
        comparison["mid_time_s"],
        comparison["control_full_median_e_s"],
        marker="o",
        label="Nominal control",
    )
    ax.set_xlabel("Interval midpoint (s)")
    ax.set_ylabel("Full-frame median interval rate (e-/s/pixel)")
    ax.set_title("Measured interval rate: contaminated versus nominal exposure")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    fig.savefig(output.with_suffix(".svg"))
    plt.close(fig)


def plot_transient_excess(
    comparison: pd.DataFrame,
    output: Path,
    *,
    threshold_e_s: float = 0.05,
) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.axhline(0.0, linewidth=1)
    ax.axhline(threshold_e_s, linewidth=1, linestyle="--", label="Engineering threshold")
    ax.plot(
        comparison["mid_time_s"],
        comparison["transient_excess_e_s"],
        marker="o",
        label="Transient excess above late-time offset",
    )
    flagged = comparison[comparison["common_mode_flag"]]
    ax.scatter(
        flagged["mid_time_s"],
        flagged["transient_excess_e_s"],
        marker="x",
        label="Common-mode flagged",
    )
    ax.set_xlabel("Interval midpoint (s)")
    ax.set_ylabel("Transient excess rate (e-/s/pixel)")
    ax.set_title("Time-variable excess relative to nominal control")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    fig.savefig(output.with_suffix(".svg"))
    plt.close(fig)
