"""Editorial, color-forward portfolio report generation for Case 001."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from weasyprint import HTML


def _build_report_hero(source: Path, destination: Path) -> Path:
    """Build a clean three-panel cover image from the first interval map row."""
    image = Image.open(source).convert("RGB")
    width, height = image.size
    boxes = [
        (0.0086, 0.0655, 0.2381, 0.2780),
        (0.3655, 0.0655, 0.5950, 0.2780),
        (0.7242, 0.0655, 0.9524, 0.2780),
    ]
    labels = ["Affected interval 0", "Nominal control", "Affected - control"]
    panels = [
        image.crop(
            (
                round(left * width),
                round(top * height),
                round(right * width),
                round(bottom * height),
            )
        )
        for left, top, right, bottom in boxes
    ]

    target_height = 520
    panels = [
        panel.resize(
            (round(panel.width * target_height / panel.height), target_height),
            Image.Resampling.LANCZOS,
        )
        for panel in panels
    ]
    gap = 24
    label_height = 48
    margin = 18
    canvas_width = sum(panel.width for panel in panels) + 2 * gap + 2 * margin
    canvas_height = label_height + target_height + 2 * margin
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
    except OSError:
        font = ImageFont.load_default()

    x_position = margin
    for panel, label in zip(panels, labels, strict=True):
        text_box = draw.textbbox((0, 0), label, font=font)
        text_width = text_box[2] - text_box[0]
        draw.text(
            (x_position + (panel.width - text_width) / 2, margin),
            label,
            fill="#172033",
            font=font,
        )
        canvas.paste(panel, (x_position, margin + label_height))
        x_position += panel.width + gap

    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, quality=95)
    return destination


def build_case_001_report(case_dir: Path, output_path: Path) -> None:
    """Build the finished nine-page Brooks Photonics Case 001 report."""
    derived = case_dir / "data" / "derived"
    figures = case_dir / "figures"
    report_assets = case_dir / "report" / "_assets"
    report_assets.mkdir(parents=True, exist_ok=True)

    summary = json.loads((derived / "case_summary.json").read_text(encoding="utf-8"))
    comparison = summary["comparison"]
    scattered = summary["scattered"]
    nominal = summary["nominal"]
    bootstrap = json.loads(
        (derived / "bootstrap_metrics.json").read_text(encoding="utf-8")
    )
    flt = json.loads(
        (derived / "flt_reconstruction_metrics.json").read_text(encoding="utf-8")
    )
    source = json.loads(
        (derived / "source_mask_metrics.json").read_text(encoding="utf-8")
    )

    common = ", ".join(map(str, comparison["common_mode_flagged_intervals"]))
    spatial = ", ".join(map(str, comparison["spatial_flagged_intervals"]))
    hero_path = _build_report_hero(
        figures / "representative_interval_maps.png",
        report_assets / "report_hero.png",
    )

    css = """
@page { size: Letter; margin: 0.58in 0.62in 0.55in 0.62in;
  @top-left { content: "BROOKS PHOTONICS  /  CASE STUDY 001"; font: 600 7.5pt "Liberation Sans"; color:#6A3FA0; letter-spacing:.08em; }
  @top-right { content: "WFC3/IR HgCdTe ramp integrity"; font: 400 7.5pt "Liberation Sans"; color:#667085; }
  @bottom-left { content: "Independent detector-data analysis"; font: 400 7pt "Liberation Sans"; color:#7A8494; }
  @bottom-right { content: counter(page); font: 500 7.5pt "Liberation Sans"; color:#556070; }
}
@page:first { @top-left { content:none } @top-right { content:none } @bottom-left { content:none } }
*{box-sizing:border-box} html{font-family:"Liberation Sans",Arial,sans-serif;color:#172033;font-size:10.2pt;line-height:1.42}
body{margin:0} .page{break-after:page; min-height:9.15in; position:relative} .page:last-child{break-after:auto}
h1,h2,h3,p{margin-top:0} h1{font-size:30pt;line-height:1.03;letter-spacing:-.035em;margin-bottom:14px;max-width:7.0in}
h2{font-size:20pt;line-height:1.12;letter-spacing:-.025em;margin-bottom:14px} h3{font-size:12.2pt;line-height:1.25;margin-bottom:7px}
.eyebrow{font-size:8.5pt;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:#6A3FA0;margin-bottom:14px}
.deck{font-size:13pt;line-height:1.38;color:#495467;max-width:6.55in;margin-bottom:19px}
.rule{height:3px;background:linear-gradient(90deg,#6A3FA0 0 19%,#D8C7E9 19% 100%);margin:8px 0 22px}
.hero{width:100%;height:2.2in;object-fit:cover;object-position:center top;border-radius:4px;display:block}
.cover-meta{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;margin-top:16px}.cover-meta .small{font-size:8.5pt;color:#667085}.date{font-size:9.5pt;font-weight:700;color:#6A3FA0}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:16px 0 22px}.metric{border-top:3px solid #6A3FA0;background:#F7F5FA;padding:10px 11px 11px;min-height:.78in}.metric.orange{border-color:#C35B2A}.metric.teal{border-color:#157A7A}.metric.blue{border-color:#2D5F9A}.metric .value{font-size:18pt;font-weight:750;letter-spacing:-.03em;line-height:1.05}.metric .label{font-size:7.8pt;color:#5D6778;margin-top:5px;line-height:1.24}
.section-tag{font-size:7.5pt;font-weight:700;letter-spacing:.12em;color:#6A3FA0;text-transform:uppercase;margin-bottom:7px}.lead{font-size:11.4pt;line-height:1.48;color:#344054;max-width:6.85in}
.callout{border-left:4px solid #6A3FA0;background:#F5F1F8;padding:13px 16px;margin:14px 0 18px;font-size:12pt;font-weight:650;line-height:1.38}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:22px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.card{border:1px solid #DDE2EA;border-radius:4px;padding:14px;background:white}.card h3{color:#243044}.card p{font-size:9.3pt;color:#4D5869;margin-bottom:0}.card .num{font-size:20pt;font-weight:750;color:#6A3FA0;margin-bottom:3px}.card.orange .num{color:#C35B2A}.card.teal .num{color:#157A7A}
.figure{width:100%;display:block}.figcap{font-size:7.7pt;color:#667085;line-height:1.35;margin-top:7px}.insight-title{font-size:17.5pt;line-height:1.18;letter-spacing:-.02em;max-width:6.7in;margin-bottom:12px}
.side-note{font-size:8.4pt;color:#667085;border-top:1px solid #CBD2DC;padding-top:8px}
.kpi-table{width:100%;border-collapse:collapse;margin-top:12px;font-size:8.7pt}.kpi-table th{background:#EFF2F6;text-align:left;padding:7px 8px;font-size:7.5pt;text-transform:uppercase;letter-spacing:.05em;color:#4E596A}.kpi-table td{padding:7px 8px;border-bottom:1px solid #E2E6EC;vertical-align:top}.kpi-table td:last-child{font-weight:700;color:#202A3A}.kpi-table tr:last-child td{border-bottom:0}
.steps{counter-reset:steps;display:grid;grid-template-columns:1fr 1fr;gap:11px 18px;margin-top:14px}.step{position:relative;padding-left:34px;min-height:44px;font-size:9pt;color:#495467}.step:before{counter-increment:steps;content:counter(steps);position:absolute;left:0;top:0;width:24px;height:24px;border-radius:50%;background:#6A3FA0;color:#fff;text-align:center;line-height:24px;font-weight:700;font-size:8.5pt}
.banner{background:#172033;color:white;padding:18px 20px;border-radius:4px;margin:15px 0}.banner .big{font-size:17pt;font-weight:700;line-height:1.25}.banner .sub{font-size:9pt;color:#D6DCE5;margin-top:7px}
.pill{display:inline-block;border-radius:999px;padding:4px 8px;background:#E9DFF4;color:#4A286F;font-weight:700;font-size:7.5pt;margin-right:5px}.pill.orange{background:#F7E4DB;color:#8C3F20}.pill.teal{background:#DCEEEE;color:#0F5E5E}
.reco{display:grid;grid-template-columns:32px 1fr;gap:10px;margin:10px 0}.reco .n{width:28px;height:28px;background:#6A3FA0;color:white;border-radius:4px;text-align:center;line-height:28px;font-weight:700}.reco h3{margin-bottom:2px}.reco p{font-size:9.1pt;color:#4D5869;margin-bottom:0}
.sources{font-size:7.7pt;color:#596475;line-height:1.42}.cover-accent{position:absolute;top:-.58in;right:-.62in;width:2.7in;height:.17in;background:linear-gradient(90deg,#6A3FA0,#C35B2A,#157A7A)}
"""

    figure_uri = {
        name: (figures / name).resolve().as_uri()
        for name in (
            "spatial_and_dq.png",
            "representative_interval_maps.png",
            "temporal_diagnosis.png",
            "robustness_summary.png",
            "flt_reconstruction.png",
        )
    }

    html_document = f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
<section class="page">
  <div class="cover-accent"></div>
  <div class="eyebrow">Public-data technical case study 001</div>
  <h1>Read-level diagnosis of time-variable contamination in a HgCdTe focal plane array</h1>
  <p class="deck">A reproducible WFC3/IR analysis showing why spatial inspection alone can miss a lower-amplitude transient tail - and how read selection changes the final count-rate product.</p>
  <img class="hero" src="{hero_path.resolve().as_uri()}">
  <div class="metrics">
    <div class="metric orange"><div class="value">{spatial}</div><div class="label">Spatially anomalous intervals</div></div>
    <div class="metric"><div class="value">{common}</div><div class="label">Common-mode intervals</div></div>
    <div class="metric teal"><div class="value">{comparison['common_mode_flagged_duration_s']:.0f} s</div><div class="label">Transient duration</div></div>
    <div class="metric blue"><div class="value">{100 * comparison['transient_excess_fraction_of_control_charge']:.1f}%</div><div class="label">Excess / nominal charge</div></div>
  </div>
  <div class="callout">The visible spatial gradient ends before the temporal contamination. A spatial-only diagnostic would terminate the anomaly too early and retain intervals with measurable control-relative excess.</div>
  <div class="cover-meta"><div class="small">Analysis by Brooks Photonics using public HST WFC3/IR measurements from MAST.<br>No client data are represented.</div><div class="date">July 2026</div></div>
</section>

<section class="page">
  <div class="section-tag">Executive summary</div>
  <h2 class="insight-title">The result is a measurement-condition diagnosis, not a detector-material diagnosis</h2>
  <div class="rule"></div>
  <div class="grid2">
    <div>
      <p class="lead">The affected exposure contains two physically distinct regimes. Intervals <b>{spatial}</b> show pronounced left-right nonuniformity. A lower-amplitude detector-wide excess continues through interval <b>{common.split(', ')[-1]}</b>, giving a total transient duration of <b>{comparison['common_mode_flagged_duration_s']:.3f} s</b>.</p>
      <div class="banner"><div class="big">Most consistent mechanism:<br><span style="color:#D9C6EE">time-variable external background</span></div><div class="sub">The effect decays during one exposure, is absent from the matched control, survives source masking, and changes the reconstructed slope.</div></div>
      <div class="steps">
        <div class="step"><b>Reconstruct charge</b><br>Convert calibrated count-rate reads into cumulative charge.</div>
        <div class="step"><b>Measure intervals</b><br>Calculate consecutive-read rates instead of trusting one final slope.</div>
        <div class="step"><b>Separate modes</b><br>Quantify spatial asymmetry and common-mode excess independently.</div>
        <div class="step"><b>Refit the ramp</b><br>Compare all-read and post-transient slopes with the archived FLT.</div>
      </div>
    </div>
    <div>
      <div class="grid2" style="gap:12px">
        <div class="card orange"><div class="num">{100 * scattered['maximum_absolute_asymmetry']:.2f}%</div><h3>Peak affected asymmetry</h3><p>Compared with {100 * nominal['maximum_absolute_asymmetry']:.2f}% in the nominal control.</p></div>
        <div class="card"><div class="num">{comparison['peak_transient_excess_e_s']:.4f}</div><h3>Peak excess rate</h3><p>e-/s/pixel after matched-control and late-offset correction.</p></div>
        <div class="card teal"><div class="num">{source['retained_fraction'] * 100:.2f}%</div><h3>Source-free pixels retained</h3><p>Classification agreement remains {source['source_free_flag_agreement_fraction'] * 100:.0f}%.</p></div>
        <div class="card"><div class="num">{bootstrap['n_bootstrap']:,}</div><h3>Bootstrap replicates</h3><p>Every run retains the nominal 700 s classification duration.</p></div>
      </div>
      <table class="kpi-table"><thead><tr><th>Decision metric</th><th>Result</th></tr></thead><tbody>
        <tr><td>Integrated full-frame excess</td><td>{comparison['integrated_transient_excess_e_per_pixel']:.2f} e-/pixel</td></tr>
        <tr><td>Robust tile-median estimate</td><td>{bootstrap['integrated_excess_point_e_per_pixel']:.2f} e-/pixel</td></tr>
        <tr><td>Bootstrap 95% interval</td><td>{bootstrap['integrated_excess_ci95_low_e_per_pixel']:.2f}-{bootstrap['integrated_excess_ci95_high_e_per_pixel']:.2f}</td></tr>
        <tr><td>Pixels ever carrying DATAREJECT</td><td>{100 * flt['ima_datareject_any_fraction']:.2f}%</td></tr>
      </tbody></table>
    </div>
  </div>
</section>

<section class="page">
  <div class="section-tag">01 / Data and method</div>
  <h2 class="insight-title">The analysis preserves read-level evidence that the pipeline itself can reject</h2>
  <p class="lead">Four public products are used: two calibrated IMA ramps and their archived FLT count-rate products. The affected and nominal exposures come from the same HST program and visit, providing a defensible matched comparison.</p>
  <div class="grid2" style="margin-top:18px">
    <div class="card"><h3>Interval-rate construction</h3><p>For calibrated read rate <i>R<sub>i</sub></i> at time <i>t<sub>i</sub></i>, cumulative charge is <b>Q<sub>i</sub> = R<sub>i</sub>t<sub>i</sub></b>. Consecutive-read rate is then <b>(Q<sub>i</sub> - Q<sub>i-1</sub>)/(t<sub>i</sub> - t<sub>i-1</sub>)</b>.</p></div>
    <div class="card"><h3>Data-quality policy</h3><p>Every standard 16-bit WFC3 DQ flag is rejected except <b>DATAREJECT = 8192</b>. That bit is retained because it is generated by ramp fitting and is diagnostically relevant, not a permanent material defect.</p></div>
  </div>
  <img class="figure" style="margin-top:18px" src="{figure_uri['spatial_and_dq.png']}">
  <div class="figcap"><b>Figure 1.</b> The early spatial asymmetry and the pipeline DATAREJECT response evolve together. Color, line style, and marker shape redundantly identify affected and control exposures.</div>
  <table class="kpi-table"><thead><tr><th>Input product</th><th>Role</th></tr></thead><tbody>
    <tr><td>icqtbbbxq_ima.fits</td><td>Affected calibrated nondestructive reads</td></tr>
    <tr><td>icqtbbc0q_ima.fits</td><td>Nominal matched-control reads</td></tr>
    <tr><td>icqtbbbxq_flt.fits</td><td>Archived affected ramp-fit comparison</td></tr>
    <tr><td>icqtbbc0q_flt.fits</td><td>Archived nominal ramp-fit comparison</td></tr>
  </tbody></table>
</section>

<section class="page">
  <div class="section-tag">02 / Spatial evolution</div>
  <h2 class="insight-title">The strong gradient collapses first; the common-mode tail persists</h2>
  <p class="lead">Representative interval maps show the transition from an obvious left-side enhancement to a detector-wide residual that is difficult to identify from spatial appearance alone.</p>
  <img class="figure" style="margin-top:12px;max-height:7.65in;object-fit:contain" src="{figure_uri['representative_interval_maps.png']}">
  <div class="figcap"><b>Figure 2.</b> Affected exposure, nominal control, and matched difference at intervals 0, 2, 6, and 10. The color scales are interval-specific so spatial structure remains visible as the transient decays.</div>
</section>

<section class="page">
  <div class="section-tag">03 / Temporal diagnosis</div>
  <h2 class="insight-title">A spatial-only criterion would stop two intervals too early</h2>
  <img class="figure" src="{figure_uri['temporal_diagnosis.png']}">
  <div class="figcap"><b>Figure 3.</b> The shaded region marks intervals 0-6, which exceed the nominal 0.05 e-/s/pixel common-mode threshold after control subtraction and late-time offset removal.</div>
  <div class="grid3" style="margin-top:14px">
    <div class="card orange"><div class="num">0-3</div><h3>Spatial regime</h3><p>Strong left-right structure is independently visible.</p></div>
    <div class="card"><div class="num">4-6</div><h3>Hidden tail</h3><p>Common-mode excess remains after spatial asymmetry subsides.</p></div>
    <div class="card teal"><div class="num">{comparison['late_time_offset_e_s']:.5f}</div><h3>Static offset removed</h3><p>e-/s/pixel estimated from the late ramp.</p></div>
  </div>
  <div class="callout">Engineering implication: read acceptance should not be based on map uniformity alone. Temporal controls are necessary even after the detector image appears spatially stable.</div>
</section>

<section class="page">
  <div class="section-tag">04 / Robustness</div>
  <h2 class="insight-title">The conclusion survives threshold, baseline, source-mask, and spatial-resampling tests</h2>
  <img class="figure" src="{figure_uri['robustness_summary.png']}">
  <div class="figcap"><b>Figure 4.</b> Threshold/baseline sensitivity and spatial block-bootstrap uncertainty. The nominal classification is not an isolated tuning outcome.</div>
  <div class="grid2" style="margin-top:14px">
    <div class="card"><h3>Source-free validation</h3><p>The late-control source mask retains <b>{100 * source['retained_fraction']:.2f}%</b> of interior pixels. Classification agreement is <b>{100 * source['source_free_flag_agreement_fraction']:.0f}%</b>, and the maximum change in interval excess is only <b>{source['maximum_source_mask_effect_e_s']:.5f} e-/s/pixel</b>.</p></div>
    <div class="card"><h3>Spatial bootstrap</h3><p><b>{bootstrap['n_spatial_tiles']}</b> independent 32 x 32 pixel tiles are resampled <b>{bootstrap['n_bootstrap']:,}</b> times. The 95% interval on integrated excess is <b>{bootstrap['integrated_excess_ci95_low_e_per_pixel']:.2f}-{bootstrap['integrated_excess_ci95_high_e_per_pixel']:.2f} e-/pixel</b>.</p></div>
  </div>
  <p class="side-note" style="margin-top:18px">Estimator note: the full-frame median and spatial tile-median answer slightly different questions. The tile estimator deliberately reduces the leverage of strongly illuminated spatial regions and is used for the robust uncertainty interval.</p>
</section>

<section class="page">
  <div class="section-tag">05 / Independent reconstruction</div>
  <h2 class="insight-title">Removing the transient regime materially changes the inferred count-rate product</h2>
  <p class="lead">A free-intercept, DQ-aware ordinary-least-squares slope is fit to cumulative charge. The post-transient fit begins at <b>{flt['clean_start_time_s']:.3f} s</b>, after interval 6.</p>
  <img class="figure" style="margin-top:12px;max-height:6.1in;object-fit:contain" src="{figure_uri['flt_reconstruction.png']}">
  <div class="figcap"><b>Figure 5.</b> Archived CALWF3 FLT, independent all-read slope, post-transient slope, and post-transient minus archived residual.</div>
  <table class="kpi-table"><thead><tr><th>Product or fit</th><th>Source-free median</th><th>Left-right asymmetry</th></tr></thead><tbody>
    <tr><td>Archived CALWF3 FLT</td><td>{flt['archived_flt_source_free_median_e_s']:.5f} e-/s/pixel</td><td>{100 * flt['archived_flt_left_right_asymmetry']:.2f}%</td></tr>
    <tr><td>Independent all-read fit</td><td>{flt['all_read_fit_source_free_median_e_s']:.5f} e-/s/pixel</td><td>{100 * flt['all_read_fit_left_right_asymmetry']:.2f}%</td></tr>
    <tr><td>Independent post-transient fit</td><td>{flt['clean_read_fit_source_free_median_e_s']:.5f} e-/s/pixel</td><td>{100 * flt['clean_read_fit_left_right_asymmetry']:.2f}%</td></tr>
  </tbody></table>
</section>

<section class="page">
  <div class="section-tag">06 / Engineering disposition</div>
  <h2 class="insight-title">Recommended acceptance rule: evaluate temporal and spatial integrity separately</h2>
  <div class="callout">The final fitted product retains measurable influence from the time-variable ramp history. The post-transient fit is {abs(flt['clean_read_vs_flt']['median_residual_e_s']):.5f} e-/s/pixel below the archived FLT median and reduces left-right asymmetry from {100 * flt['archived_flt_left_right_asymmetry']:.2f}% to {100 * flt['clean_read_fit_left_right_asymmetry']:.2f}%.</div>
  <div class="reco"><div class="n">1</div><div><h3>Inspect consecutive-read maps</h3><p>Do not accept a final slope product without reviewing interval-level spatial behavior.</p></div></div>
  <div class="reco"><div class="n">2</div><div><h3>Classify spatial and common-mode effects independently</h3><p>A detector can appear spatially stable while retaining a measurable temporal background.</p></div></div>
  <div class="reco"><div class="n">3</div><div><h3>Use a matched control or validated late-ramp baseline</h3><p>Separate a static exposure offset from a decaying transient before thresholding.</p></div></div>
  <div class="reco"><div class="n">4</div><div><h3>Quantify decision sensitivity</h3><p>Report how the classification changes across plausible thresholds and baseline windows.</p></div></div>
  <div class="reco"><div class="n">5</div><div><h3>Refit after excluding the transient regime</h3><p>Compare the reconstructed slope and residual structure against the archived or production result.</p></div></div>
  <h3 style="margin-top:22px">Mechanism assessment</h3>
  <table class="kpi-table"><thead><tr><th>Hypothesis</th><th>Assessment</th></tr></thead><tbody>
    <tr><td>Time-variable external background</td><td><span class="pill orange">Most consistent</span> Temporal decay, spatial evolution, and matched-control result agree.</td></tr>
    <tr><td>Stable gain or flat-field nonuniformity</td><td>Disfavored; expected to persist and appear similarly in the control.</td></tr>
    <tr><td>Intrinsic dark-current nonuniformity</td><td>Strongly disfavored; the detector-wide pattern decays within one exposure.</td></tr>
    <tr><td>Readout-quadrant offset</td><td>Secondary contribution possible, but insufficient to explain the smooth decay.</td></tr>
    <tr><td>Isolated cosmic-ray event</td><td>Cannot explain detector-wide, smoothly decaying background behavior.</td></tr>
  </tbody></table>
  <p class="side-note" style="margin-top:16px"><b>Interpretation boundary.</b> This case does not infer HgCdTe composition, carrier lifetime, dark-current mechanism, responsivity, detectivity, or intrinsic material quality.</p>
</section>

<section class="page">
  <div class="section-tag">Appendix / Reproducibility and sources</div>
  <h2 class="insight-title">The complete case is reproducible from pinned public products</h2>
  <div class="grid2">
    <div>
      <h3>Reproducibility controls</h3>
      <p>Exact MAST product URIs, byte counts, and SHA-256 digests are stored in the repository inventory. The workflow downloads all four products, verifies them, regenerates the analysis, runs unit and lint checks, and publishes the PDF and derived data as a GitHub Actions artifact.</p>
      <p><span class="pill">Public data</span><span class="pill teal">Pinned provenance</span><span class="pill orange">Automated verification</span></p>
      <h3 style="margin-top:22px">Primary sources</h3>
      <div class="sources">
        <p><b>STScI.</b> WFC3/IR IMA Visualization Tools with an Example of Time Variable Background.</p>
        <p><b>STScI.</b> Correcting for Scattered Light in WFC3/IR Exposures: Manually Subtracting Bad Reads.</p>
        <p><b>STScI.</b> WFC3 Data Handbook, file structure and IR calibration sections.</p>
        <p><b>MAST.</b> Public HST product archive and download API.</p>
      </div>
    </div>
    <div>
      <h3>Design and communication standard</h3>
      <p>This report uses an insight-led title hierarchy, a consistent spacing scale, direct chart annotations, and redundant visual encodings so color supports the analysis without carrying meaning alone.</p>
      <table class="kpi-table"><thead><tr><th>Output</th><th>Purpose</th></tr></thead><tbody>
        <tr><td>case_summary.json</td><td>Top-level quantified findings</td></tr>
        <tr><td>exposure_comparison.csv</td><td>Interval-level matched comparison</td></tr>
        <tr><td>threshold_sensitivity.csv</td><td>Decision robustness sweep</td></tr>
        <tr><td>bootstrap_interval_uncertainty.csv</td><td>Spatial uncertainty intervals</td></tr>
        <tr><td>flt_reconstruction_metrics.json</td><td>Archived versus independent fit comparison</td></tr>
      </tbody></table>
      <div class="banner" style="margin-top:22px"><div class="big">Brooks Photonics</div><div class="sub">Independent, physics-based analysis of infrared detector electrical, spectral, temporal, and noise data.</div></div>
    </div>
  </div>
</section>
</body></html>"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_document, base_url=str(case_dir.resolve())).write_pdf(output_path)
