"""HTML page templates for Case 001 reports."""

from __future__ import annotations

import os

from brooks_cases.report_assets import _range_text


def _client_pages(context: dict[str, object], assets: dict[str, str]) -> str:
    comparison = context["comparison"]
    scattered = context["scattered"]
    nominal = context["nominal"]
    bootstrap = context["bootstrap"]
    flt = context["flt"]
    source = context["source"]
    spatial_values = comparison["spatial_flagged_intervals"]
    common_values = comparison["common_mode_flagged_intervals"]
    spatial = _range_text(spatial_values)
    common = _range_text(common_values)
    final_common = max(common_values)
    rate_unit = "electrons s<sup>-1</sup> pixel<sup>-1</sup>"
    charge_unit = "electrons pixel<sup>-1</sup>"
    median_shift = abs(flt["clean_read_vs_flt"]["median_residual_e_s"])

    return f"""
<section class="page">
  <div class="cover-accent"></div>
  <div class="eyebrow">Public-data technical case study 001</div>
  <h1>Diagnosing a hidden ramp transient in WFC3/IR HgCdTe data</h1>
  <p class="deck">Why spatial inspection alone would accept affected reads - and bias the final count-rate product.</p>
  <img class="hero" src="{assets['hero']}">
  <div class="metrics">
    <div class="metric orange"><div class="value">{spatial}</div><div class="label">Spatially anomalous intervals</div></div>
    <div class="metric"><div class="value">{common}</div><div class="label">Common-mode intervals</div></div>
    <div class="metric teal"><div class="value">{comparison['common_mode_flagged_duration_s']:.0f} s</div><div class="label">Transient duration</div></div>
    <div class="metric blue"><div class="value">{100 * comparison['transient_excess_fraction_of_control_charge']:.1f}%</div><div class="label">Excess relative to nominal charge</div></div>
  </div>
  <div class="callout">The strong spatial gradient ends before the control-relative transient. A spatial-only diagnostic would stop two intervals too early.</div>
  <div class="cover-meta"><div class="small">Analysis by Brooks Photonics using public HST WFC3/IR measurements from MAST.<br>No client data are represented.</div><div class="date">July 2026</div></div>
</section>

<section class="page">
  <div class="section-tag">Executive conclusion and method</div>
  <h2 class="insight-title">Read-level evidence identifies a time-variable external background</h2>
  <div class="rule"></div>
  <div class="grid2">
    <div>
      <p class="lead">Intervals <b>{spatial}</b> contain pronounced left-right structure. A lower-amplitude detector-wide excess remains through interval <b>{final_common}</b>, producing a total transient duration of <b>{comparison['common_mode_flagged_duration_s']:.0f} s</b>. No intrinsic detector-material explanation is required by the data.</p>
      <div class="banner"><div class="big">Supported mechanism:<br><span style="color:#D9C6EE">time-variable external background</span></div><div class="sub">The effect decays within one exposure, is absent from the matched control, survives source masking, and changes the reconstructed slope.</div></div>
      <div class="steps">
        <div class="step"><b>Reconstruct charge</b><br>Recover cumulative charge from calibrated reads.</div>
        <div class="step"><b>Measure intervals</b><br>Calculate consecutive-read rates.</div>
        <div class="step"><b>Separate modes</b><br>Evaluate spatial and common-mode behavior independently.</div>
        <div class="step"><b>Refit the ramp</b><br>Exclude the transient and compare the result.</div>
      </div>
    </div>
    <div>
      <div class="grid2" style="gap:10px">
        <div class="card orange"><div class="num">{100 * scattered['maximum_absolute_asymmetry']:.2f}%</div><h3>Peak affected asymmetry</h3><p>{100 * nominal['maximum_absolute_asymmetry']:.2f}% in the nominal control.</p></div>
        <div class="card"><div class="num">{comparison['peak_transient_excess_e_s']:.4f}</div><h3>Peak excess rate</h3><p>{rate_unit} after control and offset correction.</p></div>
        <div class="card teal"><div class="num">{source['retained_fraction'] * 100:.2f}%</div><h3>Source-free pixels retained</h3><p>Classification agreement remains {source['source_free_flag_agreement_fraction'] * 100:.0f}%.</p></div>
        <div class="card blue"><div class="num">{bootstrap['n_bootstrap']:,}</div><h3>Bootstrap replicates</h3><p>All retain the nominal 700 s duration.</p></div>
      </div>
      <div class="commercial" style="margin-top:12px"><h3>Relevance to detector development and production</h3><ul>
        <li>Detect time-dependent artifacts hidden by final fitted outputs.</li>
        <li>Separate device nonuniformity from common-mode test conditions.</li>
        <li>Quantify decision sensitivity and uncertainty.</li>
        <li>Specify the minimum additional measurement needed to resolve ambiguity.</li>
      </ul></div>
    </div>
  </div>
</section>

<section class="page">
  <div class="section-tag">01 / Spatial evolution</div>
  <h2 class="insight-title">The gradient collapses first; the common-mode tail remains</h2>
  <p class="lead">Three decision-relevant stages show the transition from an obvious spatial anomaly to a temporally elevated but visually subtle detector state.</p>
  <img class="figure" style="margin-top:10px;max-height:7.35in;object-fit:contain" src="{assets['client_spatial']}">
  <div class="figcap"><b>Figure 1.</b> Affected exposure and affected-minus-control maps for intervals 0, 6, and 10. The map scales remain interval-specific to preserve spatial detail; quantitative acceptance is determined from the temporal analysis on the next page.</div>
</section>

<section class="page">
  <div class="section-tag">02 / Temporal diagnosis and robustness</div>
  <h2 class="insight-title">Temporal controls detect three additional affected intervals after the image appears stable</h2>
  <img class="figure" style="max-height:4.25in;object-fit:contain" src="{assets['temporal']}">
  <div class="figcap"><b>Figure 2.</b> Intervals 0 to 6 exceed the nominal 0.05 <span class="unit">{rate_unit}</span> common-mode threshold after matched-control subtraction and late-offset removal.</div>
  <img class="figure" style="margin-top:7px;max-height:3.2in;object-fit:contain" src="{assets['robustness']}">
  <div class="figcap"><b>Figure 3.</b> The decision endpoint is stable across threshold and late-baseline choices. Spatial block resampling preserves the 700 s classification duration.</div>
  <p class="side-note"><b>Estimator distinction.</b> The detector-wide median gives {comparison['integrated_transient_excess_e_per_pixel']:.2f} {charge_unit}; the spatially robust tile-median gives {bootstrap['integrated_excess_point_e_per_pixel']:.2f} {charge_unit}. These are different estimands, not competing estimates of one quantity.</p>
</section>

<section class="page">
  <div class="section-tag">03 / Independent reconstruction</div>
  <h2 class="insight-title">Removing the transient materially changes the inferred count-rate product</h2>
  <p class="lead">A free-intercept, DQ-aware ordinary-least-squares fit begins at <b>{flt['clean_start_time_s']:.3f} s</b>, after interval 6. Early excess charge is then absorbed by the intercept rather than forcing the later slope upward.</p>
  <img class="figure" style="margin-top:8px;max-height:5.85in;object-fit:contain" src="{assets['flt']}">
  <div class="figcap"><b>Figure 4.</b> Archived CALWF3 FLT, independent all-read slope, independent post-transient slope, and post-transient-minus-FLT residual.</div>
  <div class="result-strip">
    <div><div class="big">6.32% to 0.40%</div><div class="small">Left-right asymmetry after transient exclusion</div></div>
    <div><div class="big">{median_shift:.5f}</div><div class="small">Median change in {rate_unit}</div></div>
  </div>
  <table class="kpi-table"><thead><tr><th>Product or fit</th><th>Source-free median</th><th>Left-right asymmetry</th></tr></thead><tbody>
    <tr><td>Archived CALWF3 FLT</td><td>{flt['archived_flt_source_free_median_e_s']:.5f} {rate_unit}</td><td>{100 * flt['archived_flt_left_right_asymmetry']:.2f}%</td></tr>
    <tr><td>Independent all-read fit</td><td>{flt['all_read_fit_source_free_median_e_s']:.5f} {rate_unit}</td><td>{100 * flt['all_read_fit_left_right_asymmetry']:.2f}%</td></tr>
    <tr><td>Independent post-transient fit</td><td>{flt['clean_read_fit_source_free_median_e_s']:.5f} {rate_unit}</td><td>{100 * flt['clean_read_fit_left_right_asymmetry']:.2f}%</td></tr>
  </tbody></table>
</section>

<section class="page">
  <div class="section-tag">04 / Engineering disposition</div>
  <h2 class="insight-title">Acceptance should test temporal and spatial integrity separately</h2>
  <div class="grid2">
    <div>
      <div class="reco"><div class="n">1</div><div><h3>Inspect consecutive-read maps</h3><p>Do not accept a final slope product without interval-level review.</p></div></div>
      <div class="reco"><div class="n">2</div><div><h3>Classify spatial and common-mode effects independently</h3><p>A detector can appear uniform while retaining a measurable temporal background.</p></div></div>
      <div class="reco"><div class="n">3</div><div><h3>Use a matched control or validated late baseline</h3><p>Separate static offsets from decaying transients before thresholding.</p></div></div>
      <div class="reco"><div class="n">4</div><div><h3>Quantify decision sensitivity</h3><p>Report threshold, baseline, source-mask, and spatial-resampling dependence.</p></div></div>
      <div class="reco"><div class="n">5</div><div><h3>Refit after transient exclusion</h3><p>Compare slope, residual structure, and operational metrics with the production result.</p></div></div>
      <h3 style="margin-top:15px">Evidence-rating standard</h3>
      <div class="evidence-key">
        <div><b>Supported</b><span>Consistent with all principal observations.</span></div>
        <div class="secondary"><b>Plausible secondary</b><span>May contribute, but cannot explain the full result.</span></div>
        <div class="disfavored"><b>Disfavored</b><span>Conflicts with one or more major observations.</span></div>
        <div class="not-evaluated"><b>Not evaluated</b><span>Insufficient evidence in the available data.</span></div>
      </div>
    </div>
    <div>
      <table class="kpi-table" style="margin-top:0"><thead><tr><th>Mechanism</th><th>Assessment</th></tr></thead><tbody>
        <tr><td>Time-variable external background</td><td><span class="pill orange">Supported</span> Temporal decay, spatial evolution, and control comparison agree.</td></tr>
        <tr><td>Readout-quadrant offset</td><td><span class="pill">Plausible secondary</span> May contribute, but cannot explain the smooth detector-wide decay.</td></tr>
        <tr><td>Stable gain or flat-field nonuniformity</td><td><span class="pill gray">Disfavored</span> Expected to persist and appear similarly in the control.</td></tr>
        <tr><td>Intrinsic dark-current nonuniformity</td><td><span class="pill gray">Disfavored</span> The pattern decays within one exposure.</td></tr>
        <tr><td>Isolated cosmic-ray event</td><td><span class="pill gray">Disfavored</span> Cannot explain detector-wide smooth decay.</td></tr>
      </tbody></table>
      <h3 style="margin-top:14px">Data provenance</h3>
      <p style="font-size:8.5pt;color:#4F5B6D">Four pinned MAST products are verified by byte count and SHA-256. Raw FITS files remain outside Git; the repository stores exact URIs, derived tables, figures, tests, and the complete execution workflow.</p>
      <h3 style="margin-top:12px">Primary references</h3>
      <div class="sources">
        <p>[1] Space Telescope Science Institute, <i>WFC3/IR IMA Visualization Tools with an Example of Time Variable Background</i>, technical notebook.</p>
        <p>[2] Space Telescope Science Institute, <i>WFC3 Data Handbook</i>, file-structure and IR-calibration sections.</p>
        <p>[3] Mikulski Archive for Space Telescopes, public HST product archive and download API.</p>
      </div>
      <div class="cta" style="margin-top:13px"><h3>Need an independent detector-data assessment?</h3><p>Brooks Photonics analyzes electrical, spectral, temporal, and noise data to distinguish physical limitations from measurement artifacts and define the next resolving experiment.</p><div class="contact">brooks-photonics.com &nbsp; | &nbsp; terence@brooks-photonics.com</div></div>
    </div>
  </div>
  <p class="side-note" style="margin-top:12px"><b>Interpretation boundary.</b> This case does not infer HgCdTe composition, carrier lifetime, dark-current mechanism, responsivity, detectivity, or intrinsic material quality. The 0.05 <span class="unit">{rate_unit}</span> threshold is a transparent engineering criterion for this demonstration, not an official WFC3 pipeline threshold.</p>
</section>
"""


def _technical_appendix(context: dict[str, object], assets: dict[str, str]) -> str:
    inventory = context["inventory"]
    flt = context["flt"]
    commit = os.environ.get("GITHUB_SHA", "repository history")
    if commit != "repository history":
        commit = commit[:12]
    rate_unit = "electrons s<sup>-1</sup> pixel<sup>-1</sup>"
    product_rows = "".join(
        f"<tr><td>{item['filename']}</td><td>{item['bytes']:,}</td><td class='mono'>{item['sha256']}</td></tr>"
        for item in inventory
    )
    return f"""
<section class="page">
  <div class="section-tag">Technical appendix A / Method and DQ policy</div>
  <h2 class="insight-title">The analysis preserves read-level evidence that final ramp fitting can conceal</h2>
  <p class="lead">Each IMA extension is sorted into chronological order. Cumulative charge is reconstructed before consecutive-read rates are calculated, ensuring that the diagnostic operates on the physical increment between reads rather than on the final fitted slope alone.</p>
  <div class="grid2" style="margin-top:14px">
    <div>
      <h3>Charge reconstruction</h3>
      <div class="eq"><i>Q</i><sub>i</sub>(x,y) = <i>R</i><sub>i</sub>(x,y)<i>t</i><sub>i</sub></div>
      <h3>Consecutive-read interval rate</h3>
      <div class="eq"><i>q</i><sub>i</sub>(x,y) = [<i>Q</i><sub>i</sub>(x,y) - <i>Q</i><sub>i-1</sub>(x,y)] / [<i>t</i><sub>i</sub> - <i>t</i><sub>i-1</sub>]</div>
    </div>
    <div class="card"><h3>Data-quality policy</h3><p>Every standard 16-bit WFC3 DQ flag is rejected except <b>DATAREJECT = 8192</b>. DATAREJECT is generated by the up-the-ramp fit and is retained as diagnostic evidence rather than treated as a permanent detector defect.</p><p style="margin-top:8px"><b>{100 * flt['ima_datareject_any_fraction']:.2f}%</b> of affected-array pixels carry DATAREJECT in at least one read.</p></div>
  </div>
  <img class="figure" style="margin-top:15px;max-height:5.5in;object-fit:contain" src="{assets['spatial_dq']}">
  <div class="figcap"><b>Figure A1.</b> Spatial asymmetry and the pipeline DATAREJECT response evolve together. Affected and control data are encoded by color, marker, and line style.</div>
  <table class="kpi-table"><thead><tr><th>Analysis component</th><th>Implementation</th></tr></thead><tbody>
    <tr><td>Spatial statistic</td><td>Sigma-clipped full-frame, left-half, and right-half medians</td></tr>
    <tr><td>Common-mode comparison</td><td>Matched-control subtraction with late-ramp static-offset correction</td></tr>
    <tr><td>Source rejection</td><td>Late-control source mask with morphological dilation</td></tr>
    <tr><td>Uncertainty</td><td>779 spatial tiles and 2,000 block-bootstrap replicates</td></tr>
    <tr><td>Independent reconstruction</td><td>Free-intercept DQ-aware ordinary-least-squares ramp slope</td></tr>
  </tbody></table>
</section>

<section class="page">
  <div class="section-tag">Technical appendix B / Complete spatial sequence</div>
  <h2 class="insight-title">The complete interval sequence documents the transition from gradient to common mode</h2>
  <img class="figure" style="margin-top:8px;max-height:8.0in;object-fit:contain" src="{assets['full_spatial']}">
  <div class="figcap"><b>Figure B1.</b> Affected exposure, nominal control, and matched difference at intervals 0, 2, 6, and 10. Interval-specific color scales preserve late-stage spatial detail; absolute acceptance is based on the temporal statistics reported in the client report.</div>
</section>

<section class="page">
  <div class="section-tag">Technical appendix C / Provenance and reproducibility</div>
  <h2 class="insight-title">Every source product and derived result is traceable</h2>
  <p class="lead">The complete case can be regenerated from four pinned public products. The workflow verifies source files, executes the analysis, runs lint and unit tests, builds both reports, and publishes the derived package as a GitHub Actions artifact.</p>
  <table class="kpi-table provenance"><thead><tr><th>Product</th><th>Bytes</th><th>SHA-256</th></tr></thead><tbody>{product_rows}</tbody></table>
  <div class="grid2" style="margin-top:17px">
    <div>
      <h3>Primary derived products</h3>
      <table class="kpi-table"><tbody>
        <tr><td>case_summary.json</td><td>Top-level quantified findings</td></tr>
        <tr><td>exposure_comparison.csv</td><td>Interval-level matched comparison</td></tr>
        <tr><td>threshold_sensitivity.csv</td><td>Decision robustness sweep</td></tr>
        <tr><td>bootstrap_interval_uncertainty.csv</td><td>Spatial uncertainty intervals</td></tr>
        <tr><td>flt_reconstruction_metrics.json</td><td>Archived versus independent fit comparison</td></tr>
      </tbody></table>
    </div>
    <div>
      <h3>Execution record</h3>
      <table class="kpi-table"><tbody>
        <tr><td>Repository commit</td><td class="mono">{commit}</td></tr>
        <tr><td>Python package</td><td>brooks-photonics-cases 0.1.0</td></tr>
        <tr><td>Client report</td><td>Six pages</td></tr>
        <tr><td>Technical report</td><td>Nine pages</td></tr>
        <tr><td>Validation</td><td>Ruff, Pytest, product verification</td></tr>
      </tbody></table>
    </div>
  </div>
  <h3 style="margin-top:18px">References</h3>
  <div class="sources">
    <p>[1] Space Telescope Science Institute. <i>WFC3/IR IMA Visualization Tools with an Example of Time Variable Background</i>. HST technical notebook.</p>
    <p>[2] Space Telescope Science Institute. <i>Correcting for Scattered Light in WFC3/IR Exposures: Manually Subtracting Bad Reads</i>. HST technical notebook.</p>
    <p>[3] Space Telescope Science Institute. <i>WFC3 Data Handbook</i>. Sections on WFC3 file structure and IR calibration.</p>
    <p>[4] Space Telescope Science Institute. <i>WFC3 Instrument Handbook</i>. IR detector characteristics and readout.</p>
    <p>[5] Mikulski Archive for Space Telescopes. HST public product archive and download API.</p>
  </div>
  <div class="cta" style="margin-top:17px"><h3>Brooks Photonics</h3><p>Independent, physics-based analysis of infrared detector electrical, spectral, temporal, and noise data.</p><div class="contact">brooks-photonics.com &nbsp; | &nbsp; terence@brooks-photonics.com</div></div>
  <p class="side-note" style="margin-top:12px"><b>Interpretation boundary.</b> The 0.05 <span class="unit">{rate_unit}</span> threshold is a transparent engineering criterion, not an official WFC3 pipeline threshold. This case does not infer intrinsic HgCdTe material parameters.</p>
</section>
"""
