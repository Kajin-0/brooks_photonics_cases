# Final findings — Case 001

## Read-level diagnosis of time-variable contamination in a WFC3/IR HgCdTe exposure

### Executive finding

The affected WFC3/IR exposure contains two distinguishable anomaly regimes. Intervals `0–3` exhibit pronounced spatial nonuniformity, reaching `53.85%` normalized left-right asymmetry. A lower-amplitude common-mode excess persists through interval `6`, so the complete transient regime spans `700.002 s` at the stated `0.05 e-/s/pixel` engineering threshold.

The matched control has no spatially flagged intervals and reaches only `1.83%` maximum asymmetry. Source masking leaves the classification unchanged. A 2,000-replicate spatial block bootstrap classifies intervals `0–6` above threshold with at least 95% probability. The evidence supports a time-variable external background rather than stable detector nonuniformity or an intrinsic HgCdTe defect.

## Data provenance

| Role | Product | Bytes | SHA-256 |
|---|---|---:|---|
| Affected IMA ramp | `icqtbbbxq_ima.fits` | 168,261,120 | `7b8ff356c5c00a35e2576f2c81dc14ebb1c735f0cee343918b8bbf4f26494a0c` |
| Nominal IMA ramp | `icqtbbc0q_ima.fits` | 168,261,120 | `4d9db90cdb11f2c7934c412c02102528d9d184711081e706733d3b37280fd9b5` |
| Affected FLT product | `icqtbbbxq_flt.fits` | Recorded in `data/raw/inventory.json` | Recorded in `data/raw/inventory.json` |
| Nominal FLT product | `icqtbbc0q_flt.fits` | Recorded in `data/raw/inventory.json` | Recorded in `data/raw/inventory.json` |

The source products are public calibrated WFC3/IR measurements downloaded from MAST. Each IMA contains 16 calibrated reads. Excluding the zero-time sample yields 14 consecutive positive-time intervals.

## Interval-rate method

For calibrated count-rate read `R_i(x,y)` at sample time `t_i`, cumulative charge is reconstructed as

\[
Q_i(x,y)=R_i(x,y)t_i.
\]

The consecutive-read interval rate is

\[
\dot Q_i(x,y)=\frac{Q_i(x,y)-Q_{i-1}(x,y)}{t_i-t_{i-1}}.
\]

Normalized left-right asymmetry is

\[
A_i=\frac{L_i-R_i}{\tfrac{1}{2}(|L_i|+|R_i|)}.
\]

The nominal exposure is used as a matched control. A late-time static offset estimated from the final four intervals is removed:

\[
\Delta R_{\mathrm{late}}=0.02096\ \mathrm{e^-\,s^{-1}\,pixel^{-1}}.
\]

The resulting transient excess is

\[
R_{\mathrm{excess},i}=R_{\mathrm{test},i}-R_{\mathrm{control},i}-\Delta R_{\mathrm{late}}.
\]

The nominal classification threshold is `0.05 e-/s/pixel`. Sensitivity is evaluated over thresholds from `0.02` to `0.10 e-/s/pixel` and late-baseline windows of 3–6 intervals.

## Data-quality treatment

Permanent detector and calibration defect bits are rejected. `DATAREJECT=8192` is retained as a diagnostic because it is generated during up-the-ramp processing rather than representing a permanent detector defect.

| DQ metric | Affected exposure | Nominal control |
|---|---:|---:|
| Peak interval-level DATAREJECT fraction | 34.85% | 1.07% |
| Pixels carrying DATAREJECT in at least one affected read | 35.80% | — |

The initial provisional analysis excluded all nonzero DQ values. That removed a substantial portion of the affected population and produced lower apparent asymmetry and excess. The final DQ-aware analysis preserves the measurement response being investigated.

## Quantitative results

| Metric | Result |
|---|---:|
| Spatially flagged intervals | 0–3 |
| Common-mode flagged intervals | 0–6 |
| Common-mode flagged duration | 700.002 s |
| Peak affected asymmetry | 53.85% |
| Peak control asymmetry | 1.83% |
| Peak full-frame transient excess | 0.4958 e-/s/pixel |
| Full-frame integrated positive excess | 197.26 e-/pixel |
| Full-frame excess / nominal integrated charge | 16.10% |
| Late-time offset removed | 0.02096 e-/s/pixel |

Intervals `0–3` are classified as spatial plus common-mode anomalies. Intervals `4–6` remain elevated relative to the control but no longer exceed the spatial-anomaly criterion. A spatial-only diagnostic would therefore understate the transient duration.

## Source-free validation

A source-free mask was derived from late nominal-control interval maps using a 5-sigma positive-source criterion and three-pixel dilation.

| Metric | Result |
|---|---:|
| Interior pixels retained | 94.25% |
| Classification agreement with all-pixel analysis | 100% |
| Source-free integrated excess | 196.60 e-/pixel |
| Maximum source-mask change | 0.00313 e-/s/pixel |
| Median source-mask change | 7.37e-5 e-/s/pixel |

The transient classification is not driven by bright astronomical sources.

## Spatial block-bootstrap uncertainty

The robust analysis divides the detector into 779 accepted `32 x 32` pixel tiles and resamples those tiles 2,000 times.

| Bootstrap metric | Result |
|---|---:|
| High-confidence flagged intervals | 0–6 |
| Tile-median integrated excess | 150.03 e-/pixel |
| 95% interval on integrated excess | 144.61–159.50 e-/pixel |
| 95% interval on peak excess | 0.3089–0.3680 e-/s/pixel |
| 95% interval on flagged duration | 700.002–700.002 s |
| Late-time offset, 95% interval | 0.02128–0.02288 e-/s/pixel |

The tile-median estimator is lower than the full-frame estimator because it reduces the leverage of strongly illuminated spatial regions. Both estimators identify the same temporal endpoint.

## Independent ramp reconstruction

A free-intercept, DQ-aware ordinary-least-squares slope is fitted to cumulative charge. The post-transient fit begins at `702.934 s`, after the final common-mode interval.

| Product or fit | Source-free median | Left-right asymmetry |
|---|---:|---:|
| Archived CALWF3 FLT | 1.00296 e-/s/pixel | 6.32% |
| Independent all-read slope | 0.99992 e-/s/pixel | 9.55% |
| Independent post-transient slope | 0.89337 e-/s/pixel | 0.40% |

The all-read fit closely reproduces the archived FLT median, with median residual `-0.00268 e-/s/pixel` and residual NMAD `0.01786 e-/s/pixel`. The post-transient fit is lower than the archived FLT by `0.11108 e-/s/pixel`, with residual NMAD `0.05243 e-/s/pixel`.

This demonstrates that the final fitted count-rate image retains measurable influence from the time-variable ramp history. It also shows that read rejection changes both the recovered median rate and the spatial asymmetry.

## Mechanism ranking

| Hypothesis | Assessment |
|---|---|
| Time-variable external background | Most consistent: temporal decay, early spatial gradient, later common-mode tail, matched-control absence |
| Stable flat-field or gain nonuniformity | Disfavored: would persist and appear similarly in the control |
| Intrinsic dark-current nonuniformity | Strongly disfavored: does not explain the within-ramp decay and control behavior |
| Readout-quadrant offset | Secondary contribution possible but insufficient to explain temporal decay |
| Isolated cosmic-ray event | Disfavored: cannot produce a detector-wide smoothly decaying background |

## Engineering conclusion

A single fitted count-rate product compresses the temporal structure of a nondestructive ramp. Spatial appearance alone is insufficient: the visible gradient ends before the common-mode transient. Reliable diagnosis requires consecutive-read rates, matched-control or late-ramp comparison, explicit DQ semantics, threshold sensitivity, spatial uncertainty analysis, and independent refitting after the transient interval.

The result supports a measurement-condition diagnosis. It does not establish a defect in the HgCdTe material.

## Interpretation boundary

This case does not infer HgCdTe composition, carrier lifetime, dark-current mechanism, responsivity, detectivity, or intrinsic material quality. The `0.05 e-/s/pixel` threshold is a transparent engineering criterion for this demonstration, not an official WFC3 pipeline threshold.
