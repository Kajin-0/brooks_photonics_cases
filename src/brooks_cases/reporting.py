"""Programmatic portfolio-report generation for Case 001."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
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

PURPLE = colors.HexColor("#5B2A86")
DARK = colors.HexColor("#171717")
LIGHT = colors.HexColor("#F3F0F6")


def _page(canvas, document) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    canvas.setStrokeColor(PURPLE)
    canvas.line(0.65 * inch, 0.48 * inch, 7.85 * inch, 0.48 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(DARK)
    canvas.drawString(0.65 * inch, 0.28 * inch, "Brooks Photonics | Case 001")
    canvas.drawRightString(7.85 * inch, 0.28 * inch, f"Page {document.page}")
    canvas.restoreState()


def _image(path: Path, width: float) -> Image:
    image = Image(str(path), width=width)
    image.drawHeight = image.imageHeight * width / image.imageWidth
    return image


def _table(rows: list[tuple[str, str]]) -> Table:
    table = Table([["Metric", "Result"], *rows], colWidths=[4.35 * inch, 2.35 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.2),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8B8B8")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def build_case_001_report(case_dir: Path, output_path: Path) -> None:
    """Build the finished Brooks Photonics Case 001 PDF report."""
    derived = case_dir / "data" / "derived"
    figures = case_dir / "figures"
    summary = json.loads((derived / "case_summary.json").read_text(encoding="utf-8"))
    bootstrap = json.loads((derived / "bootstrap_metrics.json").read_text(encoding="utf-8"))
    flt = json.loads((derived / "flt_reconstruction_metrics.json").read_text(encoding="utf-8"))
    source = json.loads((derived / "source_mask_metrics.json").read_text(encoding="utf-8"))
    sensitivity = pd.read_csv(derived / "threshold_sensitivity.csv")
    comparison = summary["comparison"]
    common = comparison["common_mode_flagged_intervals"]
    spatial = comparison["spatial_flagged_intervals"]
    common_text = ", ".join(map(str, common)) if common else "none"
    spatial_text = ", ".join(map(str, spatial)) if spatial else "none"
    endpoint_min = int(sensitivity["last_flagged_interval"].min())
    endpoint_max = int(sensitivity["last_flagged_interval"].max())

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CaseTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=23, leading=27, textColor=DARK, spaceAfter=12))
    styles.add(ParagraphStyle(name="CaseSection", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=19, textColor=PURPLE, spaceBefore=5, spaceAfter=8))
    styles.add(ParagraphStyle(name="CaseBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13, textColor=DARK, spaceAfter=7))
    styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=DARK, backColor=LIGHT, borderColor=PURPLE, borderWidth=1, borderPadding=9, spaceBefore=7, spaceAfter=10))
    styles.add(ParagraphStyle(name="Caption", parent=styles["BodyText"], fontSize=7.7, leading=10, alignment=TA_CENTER, spaceBefore=3, spaceAfter=8))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=7.6, leading=10, textColor=DARK))

    document = SimpleDocTemplate(str(output_path), pagesize=letter, rightMargin=0.65 * inch, leftMargin=0.65 * inch, topMargin=0.62 * inch, bottomMargin=0.62 * inch, title="Brooks Photonics Case 001", author="Brooks Photonics")
    story: list[object] = [
        Spacer(1, 0.15 * inch),
        Paragraph("BROOKS PHOTONICS", styles["CaseSection"]),
        Paragraph("Case 001: Read-Level Diagnosis of Time-Variable Contamination in a HgCdTe Focal Plane Array", styles["CaseTitle"]),
        Paragraph("Independent analysis of public Hubble WFC3/IR MULTIACCUM measurements", styles["CaseBody"]),
        Paragraph("Engineering question: Which nondestructive-read intervals are contaminated, how long does the contamination persist after the obvious spatial gradient disappears, and how does read selection change the reconstructed count-rate product?", styles["Callout"]),
        _table([
            ("Public products", "2 IMA ramps + 2 FLT products"),
            ("Positive-read intervals", str(summary["scattered"]["n_intervals"])),
            ("Spatially anomalous intervals", spatial_text),
            ("Common-mode intervals at 0.05 e-/s/pixel", common_text),
            ("Peak transient excess", f"{comparison['peak_transient_excess_e_s']:.4f} e-/s/pixel"),
            ("Integrated positive excess", f"{comparison['integrated_transient_excess_e_per_pixel']:.2f} e-/pixel"),
            ("Excess / nominal integrated charge", f"{100 * comparison['transient_excess_fraction_of_control_charge']:.2f}%"),
        ]),
        Spacer(1, 0.12 * inch),
        Paragraph("Executive finding", styles["CaseSection"]),
        Paragraph("The exposure contains two anomaly regimes. The earliest reads exhibit a strong left-side enhancement, while a lower-amplitude detector-wide excess remains after the spatial distortion is no longer obvious. A spatial-uniformity check alone therefore understates the contamination duration.", styles["CaseBody"]),
        Paragraph("Matched-control subtraction, source-free masking, threshold sensitivity, spatial block bootstrap, and independent ramp reconstruction support a time-variable external background. They do not support an intrinsic HgCdTe material defect.", styles["CaseBody"]),
        Paragraph("Public-data demonstration; no client data are represented.", styles["Small"]),
        PageBreak(),
        Paragraph("1. Read-level method and spatial evolution", styles["CaseSection"]),
        Paragraph("For each calibrated read, cumulative charge is reconstructed as Q_i = R_i t_i. Consecutive-read rate is then (Q_i - Q_{i-1})/(t_i - t_{i-1}). Permanent detector-quality bits are rejected. DATAREJECT=8192 is retained as a diagnostic because it is generated by the up-the-ramp algorithm and can respond to the time-variable background itself.", styles["CaseBody"]),
        _image(figures / "representative_interval_maps.png", 7.0 * inch),
        Paragraph("Figure 1. Contaminated exposure, nominal control, and matched difference for representative intervals. Early spatial enhancement transitions into a weaker common-mode tail.", styles["Caption"]),
        PageBreak(),
        Paragraph("2. Control-relative transient diagnosis", styles["CaseSection"]),
        _image(figures / "control_comparison.png", 6.8 * inch),
        Paragraph("Figure 2. Full-frame interval rate for the affected and nominal exposures.", styles["Caption"]),
        _image(figures / "transient_excess.png", 6.8 * inch),
        Paragraph(f"Figure 3. Late-offset-corrected transient excess. Nominal common-mode classification: intervals {common_text}.", styles["Caption"]),
        _table([
            ("Common-mode duration", f"{comparison['common_mode_flagged_duration_s']:.1f} s"),
            ("Late-time static offset", f"{comparison['late_time_offset_e_s']:.5f} e-/s/pixel"),
            ("Peak asymmetry: affected / control", f"{100 * summary['scattered']['maximum_absolute_asymmetry']:.2f}% / {100 * summary['nominal']['maximum_absolute_asymmetry']:.2f}%"),
            ("Pixels ever carrying DATAREJECT", f"{100 * flt['ima_datareject_any_fraction']:.2f}%"),
        ]),
        PageBreak(),
        Paragraph("3. Robustness and uncertainty", styles["CaseSection"]),
        _image(figures / "threshold_sensitivity.png", 6.8 * inch),
        Paragraph(f"Figure 4. Across thresholds 0.02-0.10 e-/s/pixel and late baselines of 3-6 intervals, the last flagged interval ranges from {endpoint_min} to {endpoint_max}.", styles["Caption"]),
        _image(figures / "bootstrap_uncertainty.png", 6.8 * inch),
        Paragraph("Figure 5. 95% spatial block-bootstrap intervals using 32 x 32 pixel tiles.", styles["Caption"]),
        _table([
            ("Source-free pixels retained", f"{100 * source['retained_fraction']:.2f}%"),
            ("Source-free classification agreement", f"{100 * source['source_free_flag_agreement_fraction']:.1f}%"),
            ("Bootstrap tiles / replicates", f"{bootstrap['n_spatial_tiles']} / {bootstrap['n_bootstrap']}"),
            ("Integrated excess, 95% interval", f"{bootstrap['integrated_excess_ci95_low_e_per_pixel']:.2f} to {bootstrap['integrated_excess_ci95_high_e_per_pixel']:.2f} e-/pixel"),
            ("Flagged duration, 95% interval", f"{bootstrap['flagged_duration_ci95_low_s']:.1f} to {bootstrap['flagged_duration_ci95_high_s']:.1f} s"),
        ]),
        PageBreak(),
        Paragraph("4. Independent ramp reconstruction", styles["CaseSection"]),
        Paragraph("A free-intercept, DQ-aware ordinary-least-squares slope is fitted to cumulative charge. The post-transient fit begins after the final nominal common-mode interval, so accumulated early charge changes the intercept rather than forcing the later slope upward.", styles["CaseBody"]),
        _image(figures / "flt_reconstruction.png", 6.65 * inch),
        Paragraph("Figure 6. Archived CALWF3 FLT, independent all-read slope, independent post-transient slope, and post-transient-minus-FLT residual.", styles["Caption"]),
        _table([
            ("Post-transient fit begins", f"t = {flt['clean_start_time_s']:.3f} s"),
            ("Archived FLT source-free median", f"{flt['archived_flt_source_free_median_e_s']:.5f} e-/s/pixel"),
            ("Independent all-read median", f"{flt['all_read_fit_source_free_median_e_s']:.5f} e-/s/pixel"),
            ("Independent post-transient median", f"{flt['clean_read_fit_source_free_median_e_s']:.5f} e-/s/pixel"),
            ("Post-transient vs FLT residual NMAD", f"{flt['clean_read_vs_flt']['residual_nmad_e_s']:.5f} e-/s/pixel"),
        ]),
        PageBreak(),
        Paragraph("5. Engineering conclusion", styles["CaseSection"]),
        Paragraph("The anomaly is most consistent with a time-variable external background: it decays smoothly, begins with a spatial gradient, develops a common-mode tail, is absent from the matched control, and changes the slope inferred from the nondestructive ramp.", styles["Callout"]),
        _table([
            ("Time-variable external background", "Most consistent"),
            ("Stable gain or flat-field nonuniformity", "Disfavored"),
            ("Intrinsic dark-current nonuniformity", "Strongly disfavored"),
            ("Readout-quadrant offset", "Secondary contribution possible"),
            ("Isolated cosmic ray", "Cannot explain detector-wide smooth decay"),
        ]),
        Spacer(1, 0.12 * inch),
        Paragraph("Recommended disposition: inspect consecutive-read maps before accepting a final slope product; classify spatial and common-mode effects separately; use a matched control or stable late-ramp baseline; quantify threshold sensitivity; and refit after excluding the transient regime. Do not infer detector material defects until measurement-condition explanations have been rejected.", styles["CaseBody"]),
        Paragraph("Interpretation boundary: this case does not infer HgCdTe composition, carrier lifetime, dark-current mechanism, detectivity, or intrinsic material quality.", styles["CaseBody"]),
        Paragraph("Primary references: STScI WFC3/IR IMA Visualization Tools; WFC3 Data Handbook Sections 2.2, 3.3, and 7.10; STScI scattered-light correction notebook.", styles["Small"]),
        Spacer(1, 0.2 * inch),
        Paragraph("Brooks Photonics | Independent physics-based infrared detector analysis | brooks-photonics.com | terence@brooks-photonics.com", styles["Small"]),
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.build(story, onFirstPage=_page, onLaterPages=_page)
