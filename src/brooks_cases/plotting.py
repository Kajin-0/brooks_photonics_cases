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
    ax.scatter(flagged["mid_time_s"], flagged["full_median_e_s"], marker="x", label="Flagged")
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
