"""Print-first portfolio-report generation for Case 001."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image as PILImage
from PIL import ImageEnhance, ImageOps
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

INK = "#202020"
TEXT = "#303030"
MUTED = "#6A6A6A"
ACCENT = "#6B5A73"
MID = "#8A8A8A"
GRID = "#D8D8D8"
PAPER_GRAY = "#F3F3F3"
PALE = "#F8F8F8"
WHITE = "#FFFFFF"

ACCENT_COLOR = colors.HexColor(ACCENT)
INK_COLOR = colors.HexColor(INK)
TEXT_COLOR = colors.HexColor(TEXT)
MUTED_COLOR = colors.HexColor(MUTED)
GRID_COLOR = colors.HexColor(GRID)
PAPER_COLOR = colors.HexColor(PAPER_GRAY)
PALE_COLOR = colors.HexColor(PALE)


def _set_plot_defaults() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.6,
            "axes.titlesize": 9.5,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.8,
            "ytick.labelsize": 7.8,
            "legend.fontsize": 7.5,
            "figure.facecolor": WHITE,
            "axes.facecolor": WHITE,
            "savefig.facecolor": WHITE,
            "axes.edgecolor": INK,
            "axes.labelcolor": TEXT,
            "xtick.color": TEXT,
            "ytick.color": TEXT,
            "text.color": TEXT,
        }
    )


def _finish_axes(axis) -> None:  # type: ignore[no-untyped-def]
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_linewidth(0.7)
    axis.spines["bottom"].set_linewidth(0.7)
    axis.grid(True, color=GRID, linewidth=0.55, alpha=0.65)
    axis.set_axisbelow(True)


def _save_plot(figure, path: Path) -> Path:  # type: ignore[no-untyped-def]
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=240, bbox_inches="tight", pad_inches=0.08)
    plt.close(figure)
    return path


def _build_report_charts(derived: Path, assets: Path) -> dict[str, Path]:
    _set_plot_defaults()
    comparison = pd.read_csv(derived / "exposure_comparison.csv")
    sensitivity = pd.read_csv(derived / "threshold_sensitivity.csv")
    bootstrap = pd.read_csv(derived / "bootstrap_interval_uncertainty.csv")

    figure, axis = plt.subplots(figsize=(7.25, 3.35))
    axis.plot(
        comparison["mid_time_s"],
        comparison["test_full_median_e_s"],
        marker="o",
        markersize=3.8,
        linewidth=1.6,
        color=ACCENT,
        label="Affected exposure",
    )
    axis.plot(
        comparison["mid_time_s"],
        comparison["control_full_median_e_s"],
        marker="s",
        markersize=3.2,
        linewidth=1.35,
        linestyle="--",
        color=INK,
        label="Nominal control",
    )
    axis.set_xlabel("Interval midpoint (s)")
    axis.set_ylabel("Median interval rate (e-/s/pixel)")
    axis.legend(frameon=False, loc="upper right", ncol=2)
    _finish_axes(axis)
    figure.tight_layout()
    control_path = _save_plot(figure, assets / "control_comparison_print.png")

    figure, axis = plt.subplots(figsize=(7.25, 3.2))
    axis.axhline(0.0, color=MID, linewidth=0.8)
    axis.axhline(
        0.05,
        color=INK,
        linewidth=0.9,
        linestyle=(0, (4, 3)),
        label="0.05 engineering threshold",
    )
    axis.plot(
        comparison["mid_time_s"],
        comparison["transient_excess_e_s"],
        marker="o",
        markersize=3.8,
        linewidth=1.6,
        color=ACCENT,
        label="Control-relative transient excess",
    )
    flagged = comparison[comparison["common_mode_flag"]]
    axis.scatter(
        flagged["mid_time_s"],
        flagged["transient_excess_e_s"],
        marker="x",
        s=28,
        linewidth=0.9,
        color=INK,
        label="Flagged interval",
    )
    axis.set_xlabel("Interval midpoint (s)")
    axis.set_ylabel("Transient excess (e-/s/pixel)")
    axis.legend(frameon=False, loc="upper right")
    _finish_axes(axis)
    figure.tight_layout()
    transient_path = _save_plot(figure, assets / "transient_excess_print.png")

    figure, axis = plt.subplots(figsize=(7.25, 3.25))
    line_styles = {
        3: (MID, "--", 1.0, 0.8),
        4: (ACCENT, "-", 1.7, 1.0),
        5: ("#545454", "-.", 1.15, 0.9),
        6: ("#A0A0A0", ":", 1.3, 0.9),
    }
    for late_intervals, group in sensitivity.groupby("late_intervals"):
        color, linestyle, linewidth, alpha = line_styles[int(late_intervals)]
        axis.plot(
            group["threshold_e_s"],
            group["last_flagged_interval"],
            marker="o",
            markersize=3.0,
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
            alpha=alpha,
            label=f"{int(late_intervals)}-interval late baseline",
        )
    axis.axvline(0.05, color=INK, linewidth=0.8, linestyle=(0, (3, 3)))
    axis.set_xlabel("Transient threshold (e-/s/pixel)")
    axis.set_ylabel("Last flagged interval")
    axis.set_yticks(range(-1, int(sensitivity["last_flagged_interval"].max()) + 1))
    axis.legend(frameon=False, loc="upper right", ncol=2)
    _finish_axes(axis)
    figure.tight_layout()
    threshold_path = _save_plot(figure, assets / "threshold_sensitivity_print.png")

    figure, axis = plt.subplots(figsize=(7.25, 3.25))
    x_values = comparison["mid_time_s"].to_numpy()
    axis.fill_between(
        x_values,
        bootstrap["ci95_low_e_s"],
        bootstrap["ci95_high_e_s"],
        color="#D9D6DB",
        alpha=1.0,
        label="95% spatial block-bootstrap interval",
    )
    axis.plot(
        x_values,
        bootstrap["point_transient_excess_e_s"],
        marker="o",
        markersize=3.6,
        linewidth=1.55,
        color=ACCENT,
        label="Source-free tile-median estimate",
    )
    axis.axhline(
        0.05,
        color=INK,
        linewidth=0.9,
        linestyle=(0, (4, 3)),
        label="0.05 threshold",
    )
    axis.axhline(0.0, color=MID, linewidth=0.7)
    axis.set_xlabel("Interval midpoint (s)")
    axis.set_ylabel("Transient excess (e-/s/pixel)")
    axis.legend(frameon=False, loc="upper right")
    _finish_axes(axis)
    figure.tight_layout()
    bootstrap_path = _save_plot(figure, assets / "bootstrap_uncertainty_print.png")

    return {
        "control": control_path,
        "transient": transient_path,
        "threshold": threshold_path,
        "bootstrap": bootstrap_path,
    }


def _grayscale_image(source: Path, destination: Path, contrast: float) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    image = PILImage.open(source).convert("L")
    image = ImageOps.autocontrast(image, cutoff=0.3)
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image.convert("RGB").save(destination, quality=95)
    return destination


def _report_image(path: Path, width: float) -> Image:
    image = Image(str(path), width=width)
    image.drawHeight = image.imageHeight * width / image.imageWidth
    return image


def _page_decor(canvas, document) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    width, height = letter
    if document.page > 1:
        canvas.setFont("Helvetica", 7.2)
        canvas.setFillColor(MUTED_COLOR)
        canvas.drawString(
            0.72 * inch,
            height - 0.43 * inch,
            "BROOKS PHOTONICS | CASE STUDY 001",
        )
        canvas.drawRightString(
            width - 0.72 * inch,
            height - 0.43 * inch,
            "WFC3/IR HgCdTe ramp integrity",
        )
        canvas.setStrokeColor(GRID_COLOR)
        canvas.setLineWidth(0.35)
        canvas.line(
            0.72 * inch,
            height - 0.50 * inch,
            width - 0.72 * inch,
            height - 0.50 * inch,
        )
    canvas.setStrokeColor(GRID_COLOR)
    canvas.setLineWidth(0.35)
    canvas.line(0.72 * inch, 0.47 * inch, width - 0.72 * inch, 0.47 * inch)
    canvas.setFillColor(MUTED_COLOR)
    canvas.setFont("Helvetica", 7.0)
    canvas.drawString(
        0.72 * inch,
        0.28 * inch,
        "Brooks Photonics | Independent detector-data analysis",
    )
    canvas.drawRightString(width - 0.72 * inch, 0.28 * inch, str(document.page))
    canvas.restoreState()


def build_case_001_report(case_dir: Path, output_path: Path) -> None:
    """Build a restrained, print-first Brooks Photonics Case 001 report."""
    derived = case_dir / "data" / "derived"
    figures = case_dir / "figures"
    assets = case_dir / "report" / "_assets"

    summary = json.loads((derived / "case_summary.json").read_text(encoding="utf-8"))
    bootstrap = json.loads(
        (derived / "bootstrap_metrics.json").read_text(encoding="utf-8")
    )
    flt = json.loads(
        (derived / "flt_reconstruction_metrics.json").read_text(encoding="utf-8")
    )
    source = json.loads(
        (derived / "source_mask_metrics.json").read_text(encoding="utf-8")
    )
    sensitivity = pd.read_csv(derived / "threshold_sensitivity.csv")
    comparison = summary["comparison"]
    common = comparison["common_mode_flagged_intervals"]
    spatial = comparison["spatial_flagged_intervals"]
    common_text = f"{min(common)}-{max(common)}" if common else "none"
    spatial_text = f"{min(spatial)}-{max(spatial)}" if spatial else "none"
    endpoint_min = int(sensitivity["last_flagged_interval"].min())
    endpoint_max = int(sensitivity["last_flagged_interval"].max())

    charts = _build_report_charts(derived, assets)
    representative_maps = _grayscale_image(
        figures / "representative_interval_maps.png",
        assets / "representative_interval_maps_print.png",
        1.05,
    )
    flt_maps = _grayscale_image(
        figures / "flt_reconstruction.png",
        assets / "flt_reconstruction_print.png",
        1.08,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverKicker",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.6,
            leading=10,
            textColor=ACCENT_COLOR,
            spaceAfter=12,
            tracking=0.7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=24.5,
            textColor=INK_COLOR,
            alignment=TA_LEFT,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSub",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10.2,
            leading=14.2,
            textColor=MUTED_COLOR,
            spaceAfter=16,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=13.2,
            leading=16,
            textColor=INK_COLOR,
            spaceBefore=2,
            spaceAfter=7,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.6,
            leading=9,
            textColor=ACCENT_COLOR,
            spaceAfter=3,
            tracking=0.5,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.1,
            leading=13.0,
            textColor=TEXT_COLOR,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Caption",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.4,
            leading=9.5,
            textColor=MUTED_COLOR,
            alignment=TA_LEFT,
            spaceBefore=4,
            spaceAfter=9,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.4,
            leading=9.8,
            textColor=MUTED_COLOR,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MetricValue",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11.5,
            textColor=INK_COLOR,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MetricLabel",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.2,
            leading=10.5,
            textColor=TEXT_COLOR,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CalloutText",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.2,
            leading=14.0,
            textColor=INK_COLOR,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableHead",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.7,
            leading=9.5,
            textColor=INK_COLOR,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.0,
            leading=10.3,
            textColor=TEXT_COLOR,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableBodyBold",
            parent=styles["TableBody"],
            fontName="Helvetica-Bold",
        )
    )

    def paragraph(text: str, style: str = "Body") -> Paragraph:
        return Paragraph(text, styles[style])

    def section(number: str, title: str) -> list[object]:
        rule = Table(
            [[""]],
            colWidths=[7.0 * inch],
            rowHeights=[1.1],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), ACCENT_COLOR),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            ),
        )
        return [
            Paragraph(f"SECTION {number}", styles["SectionLabel"]),
            Paragraph(title, styles["Section"]),
            rule,
            Spacer(1, 0.10 * inch),
        ]

    def clean_table(
        rows: list[tuple[str, str]],
        widths: tuple[float, float] = (4.55, 2.25),
        header: tuple[str, str] = ("Metric", "Result"),
        compact: bool = False,
    ) -> Table:
        data = [
            [paragraph(header[0], "TableHead"), paragraph(header[1], "TableHead")]
        ]
        for left, right in rows:
            data.append(
                [paragraph(left, "TableBodyBold"), paragraph(right, "TableBody")]
            )
        table = Table(
            data,
            colWidths=[widths[0] * inch, widths[1] * inch],
            repeatRows=1,
            hAlign="LEFT",
        )
        padding = 3.8 if compact else 4.8
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), PAPER_COLOR),
                    (
                        "LINEBELOW",
                        (0, 0),
                        (-1, 0),
                        0.8,
                        colors.HexColor("#6B6B6B"),
                    ),
                    ("LINEBELOW", (0, 1), (-1, -2), 0.25, GRID_COLOR),
                    (
                        "LINEBELOW",
                        (0, -1),
                        (-1, -1),
                        0.55,
                        colors.HexColor("#8C8C8C"),
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, PALE_COLOR],
                    ),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), padding),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
                ]
            )
        )
        return table

    def callout(text: str) -> Table:
        table = Table(
            [[paragraph(text, "CalloutText")]],
            colWidths=[6.86 * inch],
            hAlign="LEFT",
        )
        table.setStyle(
            TableStyle(
                [
                    ("LINEBEFORE", (0, 0), (0, 0), 2.4, ACCENT_COLOR),
                    ("LINEABOVE", (0, 0), (0, 0), 0.35, GRID_COLOR),
                    ("LINEBELOW", (0, 0), (0, 0), 0.35, GRID_COLOR),
                    ("BACKGROUND", (0, 0), (0, 0), colors.white),
                    ("LEFTPADDING", (0, 0), (0, 0), 10),
                    ("RIGHTPADDING", (0, 0), (0, 0), 8),
                    ("TOPPADDING", (0, 0), (0, 0), 8),
                    ("BOTTOMPADDING", (0, 0), (0, 0), 8),
                ]
            )
        )
        return table

    def metric_strip(items: list[tuple[str, str]]) -> Table:
        row = []
        for value, label in items:
            inner = Table(
                [
                    [paragraph(value, "MetricValue")],
                    [paragraph(label, "MetricLabel")],
                ],
                colWidths=[1.58 * inch],
            )
            inner.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    ]
                )
            )
            row.append(inner)
        table = Table([row], colWidths=[1.72 * inch] * 4, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LINEBEFORE", (1, 0), (-1, 0), 0.45, GRID_COLOR),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("BACKGROUND", (0, 0), (-1, -1), PALE_COLOR),
                    ("BOX", (0, 0), (-1, -1), 0.45, GRID_COLOR),
                ]
            )
        )
        return table

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=0.72 * inch,
        rightMargin=0.72 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.62 * inch,
        title="Brooks Photonics Case 001 - WFC3/IR ramp anomaly diagnosis",
        author="Brooks Photonics",
        subject="Independent analysis of public WFC3/IR HgCdTe detector measurements",
    )

    story: list[object] = [
        Spacer(1, 0.08 * inch),
        paragraph("BROOKS PHOTONICS / PUBLIC-DATA CASE STUDY 001", "CoverKicker"),
        paragraph(
            "Read-Level Diagnosis of Time-Variable Contamination in a HgCdTe "
            "Focal Plane Array",
            "CoverTitle",
        ),
        paragraph(
            "Independent analysis of Hubble WFC3/IR MULTIACCUM measurements",
            "CoverSub",
        ),
        callout(
            "The affected ramp contains a strong early spatial gradient followed by a "
            "lower-amplitude common-mode tail. The spatial artifact ends before the "
            "temporal contamination, and read selection materially changes the "
            "reconstructed count-rate product."
        ),
        Spacer(1, 0.14 * inch),
        metric_strip(
            [
                (spatial_text, "Spatially anomalous intervals"),
                (common_text, "Common-mode intervals"),
                (
                    f"{comparison['common_mode_flagged_duration_s']:.0f} s",
                    "Transient duration",
                ),
                (
                    f"{100 * comparison['transient_excess_fraction_of_control_charge']:.1f}%",
                    "Excess / nominal charge",
                ),
            ]
        ),
        Spacer(1, 0.18 * inch),
        clean_table(
            [
                ("Data products", "2 public IMA ramps and 2 archived FLT products"),
                (
                    "Detector read structure",
                    f"16 reads; {summary['scattered']['n_intervals']} positive-time intervals",
                ),
                (
                    "Peak control-relative excess",
                    f"{comparison['peak_transient_excess_e_s']:.4f} e-/s/pixel",
                ),
                (
                    "Integrated detector-wide excess",
                    f"{comparison['integrated_transient_excess_e_per_pixel']:.2f} e-/pixel",
                ),
                (
                    "Robust tile-median estimate",
                    f"{bootstrap['integrated_excess_point_e_per_pixel']:.2f} e-/pixel",
                ),
                (
                    "Bootstrap 95% interval",
                    f"{bootstrap['integrated_excess_ci95_low_e_per_pixel']:.2f}-"
                    f"{bootstrap['integrated_excess_ci95_high_e_per_pixel']:.2f} e-/pixel",
                ),
            ]
        ),
        Spacer(1, 0.18 * inch),
        paragraph(
            "<b>Engineering conclusion.</b> The combined temporal, spatial, "
            "control-relative, source-free, bootstrap, and refitting evidence is most "
            "consistent with a time-variable external background. It does not support "
            "an intrinsic HgCdTe material defect."
        ),
        Spacer(1, 0.09 * inch),
        paragraph(
            "<b>Scope.</b> Public-data technical demonstration. No client data are "
            "represented. The analysis does not infer composition, carrier lifetime, "
            "dark-current mechanism, responsivity, detectivity, or intrinsic material "
            "quality.",
            "Small",
        ),
        Spacer(1, 0.20 * inch),
        paragraph(
            "Prepared by Brooks Photonics | brooks-photonics.com | July 2026",
            "Small",
        ),
        PageBreak(),
    ]

    story.extend(section("01", "Data, read-level method, and spatial evolution"))
    story.extend(
        [
            paragraph(
                "The case uses two calibrated WFC3/IR IMA ramps and their archived FLT "
                "products from HST program 14037, visit BB. The affected exposure is "
                "independently compared with a nominal exposure from the same visit. "
                "Exact MAST URIs, byte counts, and SHA-256 hashes are retained in the "
                "reproducibility inventory."
            ),
            paragraph(
                "For calibrated read rate <i>R</i><sub>i</sub>(x,y) at sample time "
                "<i>t</i><sub>i</sub>, cumulative charge is reconstructed as "
                "<i>Q</i><sub>i</sub> = <i>R</i><sub>i</sub><i>t</i><sub>i</sub>. "
                "Consecutive-read interval rate is then "
                "[<i>Q</i><sub>i</sub> - <i>Q</i><sub>i-1</sub>] / "
                "[<i>t</i><sub>i</sub> - <i>t</i><sub>i-1</sub>]."
            ),
            clean_table(
                [
                    (
                        "Chronology",
                        "IMA read extensions are sorted by increasing sample time.",
                    ),
                    (
                        "DQ policy",
                        "All standard 16-bit WFC3 flags are rejected except "
                        "DATAREJECT=8192.",
                    ),
                    (
                        "Why retain DATAREJECT",
                        "It is generated by ramp fitting and is diagnostic evidence, not a "
                        "permanent detector defect.",
                    ),
                    (
                        "Spatial statistics",
                        "Sigma-clipped full-frame, left-half, and right-half medians.",
                    ),
                    (
                        "Control subtraction",
                        "Matched interval rate minus nominal control and late-time static "
                        "offset.",
                    ),
                ],
                compact=True,
            ),
            Spacer(1, 0.10 * inch),
            _report_image(representative_maps, 4.55 * inch),
            paragraph(
                "<b>Figure 1.</b> Representative instantaneous interval-rate maps for "
                "the affected exposure, nominal control, and matched difference. The "
                "strong early gradient transitions into a weaker detector-wide tail.",
                "Caption",
            ),
            PageBreak(),
        ]
    )

    story.extend(section("02", "Control-relative transient diagnosis"))
    story.extend(
        [
            _report_image(charts["control"], 6.95 * inch),
            paragraph(
                "<b>Figure 2.</b> Full-frame interval rate. The affected exposure begins "
                "well above the nominal control and decays toward it through the ramp.",
                "Caption",
            ),
            _report_image(charts["transient"], 6.95 * inch),
            paragraph(
                f"<b>Figure 3.</b> Late-offset-corrected transient excess. Intervals "
                f"{common_text} exceed the nominal 0.05 e-/s/pixel engineering threshold.",
                "Caption",
            ),
            clean_table(
                [
                    ("Spatially anomalous intervals", spatial_text),
                    ("Common-mode anomalous intervals", common_text),
                    (
                        "Peak affected / control asymmetry",
                        f"{100 * summary['scattered']['maximum_absolute_asymmetry']:.2f}% / "
                        f"{100 * summary['nominal']['maximum_absolute_asymmetry']:.2f}%",
                    ),
                    (
                        "Late-time static offset removed",
                        f"{comparison['late_time_offset_e_s']:.5f} e-/s/pixel",
                    ),
                    (
                        "Pixels ever carrying DATAREJECT",
                        f"{100 * flt['ima_datareject_any_fraction']:.2f}%",
                    ),
                ],
                compact=True,
            ),
            PageBreak(),
        ]
    )

    story.extend(section("03", "Robustness, source masking, and uncertainty"))
    story.extend(
        [
            _report_image(charts["threshold"], 6.95 * inch),
            paragraph(
                f"<b>Figure 4.</b> Threshold and baseline sensitivity. Across the "
                f"complete sweep, the last flagged interval ranges from {endpoint_min} "
                f"to {endpoint_max}; the nominal setting classifies interval 6 as the "
                "endpoint.",
                "Caption",
            ),
            _report_image(charts["bootstrap"], 6.95 * inch),
            paragraph(
                "<b>Figure 5.</b> Spatial block-bootstrap interval. All 2,000 resamples "
                "preserve the 700.002 s nominal classification duration.",
                "Caption",
            ),
            clean_table(
                [
                    (
                        "Source-free pixels retained",
                        f"{100 * source['retained_fraction']:.2f}%",
                    ),
                    (
                        "Source-free classification agreement",
                        f"{100 * source['source_free_flag_agreement_fraction']:.1f}%",
                    ),
                    (
                        "Spatial tiles / bootstrap replicates",
                        f"{bootstrap['n_spatial_tiles']} / {bootstrap['n_bootstrap']}",
                    ),
                    (
                        "Integrated excess, 95% interval",
                        f"{bootstrap['integrated_excess_ci95_low_e_per_pixel']:.2f}-"
                        f"{bootstrap['integrated_excess_ci95_high_e_per_pixel']:.2f} e-/pixel",
                    ),
                    (
                        "Peak excess, 95% interval",
                        f"{bootstrap['peak_excess_ci95_low_e_s']:.4f}-"
                        f"{bootstrap['peak_excess_ci95_high_e_s']:.4f} e-/s/pixel",
                    ),
                ],
                compact=True,
            ),
            PageBreak(),
        ]
    )

    story.extend(section("04", "Independent ramp reconstruction and FLT comparison"))
    story.extend(
        [
            paragraph(
                "A free-intercept, DQ-aware ordinary-least-squares slope is fit to "
                "cumulative charge. The post-transient fit begins after interval 6. "
                "Earlier excess charge can change the fitted intercept without forcing "
                "the later steady-state slope upward."
            ),
            _report_image(flt_maps, 6.6 * inch),
            paragraph(
                "<b>Figure 6.</b> Archived CALWF3 FLT, independent all-read fit, "
                "independent post-transient fit, and post-transient-minus-FLT residual. "
                "Images are rendered in grayscale for print inspection.",
                "Caption",
            ),
            clean_table(
                [
                    (
                        "Post-transient fit begins",
                        f"t = {flt['clean_start_time_s']:.3f} s",
                    ),
                    (
                        "Archived FLT source-free median",
                        f"{flt['archived_flt_source_free_median_e_s']:.5f} e-/s/pixel",
                    ),
                    (
                        "Independent all-read median",
                        f"{flt['all_read_fit_source_free_median_e_s']:.5f} e-/s/pixel",
                    ),
                    (
                        "Independent post-transient median",
                        f"{flt['clean_read_fit_source_free_median_e_s']:.5f} e-/s/pixel",
                    ),
                    (
                        "Post-transient minus FLT median residual",
                        f"{flt['clean_read_vs_flt']['median_residual_e_s']:.5f} e-/s/pixel",
                    ),
                    (
                        "Post-transient vs FLT residual NMAD",
                        f"{flt['clean_read_vs_flt']['residual_nmad_e_s']:.5f} e-/s/pixel",
                    ),
                ],
                compact=True,
            ),
            PageBreak(),
        ]
    )

    story.extend(section("05", "Engineering interpretation and recommended disposition"))
    story.extend(
        [
            callout(
                "The obvious spatial gradient ends before the common-mode transient. A "
                "spatial-only diagnostic would terminate the anomaly too early and retain "
                "intervals with measurable control-relative excess."
            ),
            Spacer(1, 0.12 * inch),
            clean_table(
                [
                    (
                        "Time-variable external background",
                        "Most consistent with the observed temporal decay and spatial "
                        "evolution.",
                    ),
                    (
                        "Stable gain or flat-field nonuniformity",
                        "Disfavored; it should persist through the ramp and appear similarly "
                        "in the control.",
                    ),
                    (
                        "Intrinsic dark-current nonuniformity",
                        "Strongly disfavored; the detector-wide pattern decays during one "
                        "exposure.",
                    ),
                    (
                        "Readout-quadrant offset",
                        "A secondary contribution is possible but does not explain the smooth "
                        "decay.",
                    ),
                    (
                        "Isolated cosmic-ray event",
                        "Cannot explain a detector-wide, smoothly decaying background.",
                    ),
                ],
                widths=(2.6, 4.2),
                header=("Hypothesis", "Assessment"),
            ),
            Spacer(1, 0.16 * inch),
            paragraph("Recommended disposition", "Section"),
            paragraph(
                "1. Inspect consecutive-read maps before accepting the final slope product. "
                "2. Classify spatial and common-mode effects separately. 3. Use a matched "
                "control or stable late-ramp baseline. 4. Report threshold and baseline "
                "sensitivity. 5. Refit after excluding the transient regime and compare the "
                "result with the archived product."
            ),
            paragraph(
                "<b>Interpretation boundary.</b> Do not infer a detector material defect "
                "until measurement-condition explanations have been rejected. This case "
                "does not estimate composition, lifetime, responsivity, detectivity, or "
                "intrinsic material quality."
            ),
            Spacer(1, 0.08 * inch),
            paragraph("Primary sources", "Section"),
            paragraph(
                "STScI WFC3/IR IMA Visualization Tools; STScI scattered-light correction "
                "notebook; WFC3 Data Handbook, file structure and IR calibration sections; "
                "public products obtained from MAST. Brooks Photonics is not affiliated "
                "with or endorsed by NASA, ESA, or STScI.",
                "Small",
            ),
            Spacer(1, 0.16 * inch),
            paragraph(
                "Brooks Photonics | brooks-photonics.com | Independent physics-based "
                "infrared detector analysis",
                "Small",
            ),
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.build(story, onFirstPage=_page_decor, onLaterPages=_page_decor)
