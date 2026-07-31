# Draft findings — Case 001

## Read-level diagnosis of time-variable contamination in a WFC3/IR HgCdTe exposure

### Executive finding

The contaminated WFC3/IR exposure contains two distinguishable anomaly regimes. The first three read intervals exhibit pronounced spatial nonuniformity, reaching a normalized left-right asymmetry of `19.04%`. A lower-amplitude common-mode excess persists beyond the spatially obvious regime: seven intervals, covering approximately `700.0 s`, exceed the provisional control-relative threshold of `0.05 e-/s/pixel`.

The nominal comparison exposure contains no spatially flagged intervals and reaches only `1.83%` maximum absolute asymmetry. The evidence therefore supports a time-variable external background rather than a stable detector nonuniformity or intrinsic HgCdTe defect.

## Data provenance

| Role | Product | Bytes | SHA-256 |
|---|---|---:|---|
| Contaminated IMA ramp | `icqtbbbxq_ima.fits` | 168,261,120 | `7b8ff356c5c00a35e2576f2c81dc14ebb1c735f0cee343918b8bbf4f26494a0c` |
| Nominal IMA ramp | `icqtbbc0q_ima.fits` | 168,261,120 | `4d9db90cdb11f2c7934c412c02102528d9d184711081e706733d3b37280fd9b5` |

Both products are public calibrated WFC3/IR IMA files downloaded from MAST. Each contains 16 calibrated reads. After excluding the zero-time sample, the analysis produces 14 consecutive positive-time intervals.

## Method

For calibrated count-rate read `R_i(x,y)` at sample time `t_i`, cumulative charge is reconstructed as

\[
Q_i(x,y)=R_i(x,y)t_i.
\]

The interval charge rate is

\[
\dot Q_i(x,y)=\frac{Q_i(x,y)-Q_{i-1}(x,y)}{t_i-t_{i-1}}.
\]

For each interval, the workflow excludes edge regions and pixels carrying nonzero data-quality flags, then computes sigma-clipped full-frame, left-half, and right-half medians. Normalized spatial asymmetry is

\[
A_i=\frac{L_i-R_i}{\tfrac{1}{2}(|L_i|+|R_i|)}.
\]

The nominal exposure is used as a control. The control-relative full-frame difference is corrected by the median of the final four intervals, producing a late-time static offset of

\[
\Delta R_{\mathrm{late}}=0.01919\ \mathrm{e^-\,s^{-1}\,pixel^{-1}}.
\]

The transient excess is then

\[
R_{\mathrm{excess},i}=R_{\mathrm{test},i}-R_{\mathrm{control},i}-\Delta R_{\mathrm{late}}.
\]

A provisional engineering threshold of `0.05 e-/s/pixel` is applied to the transient excess. This is an explicit analysis threshold, not an official STScI or WFC3 pipeline criterion.

## Quantitative results

| Metric | Result |
|---|---:|
| Spatially flagged intervals | 0, 1, 2 |
| Common-mode flagged intervals | 0–6 |
| Common-mode flagged duration | 700.002 s |
| Peak contaminated left-right asymmetry | 19.04% |
| Peak nominal-control asymmetry | 1.83% |
| Peak transient excess | 0.3264 e-/s/pixel |
| Integrated positive transient excess | 146.25 e-/pixel |
| Excess relative to integrated nominal-control charge | 11.93% |
| Late-time static offset removed | 0.01919 e-/s/pixel |

The first three interval classifications are `common-mode + spatial`. Intervals 3–6 are `common-mode`: they remain elevated relative to the control but no longer show a strong left-right signature. The remaining intervals fall below the provisional common-mode threshold.

## Mechanism ranking

| Hypothesis | Consistency with observations | Assessment |
|---|---|---|
| Time-variable external background | Strong temporal decay; early spatial gradient; later common-mode tail; official case provenance | Most consistent |
| Stable flat-field or gain nonuniformity | Would be expected to persist through the full ramp and appear similarly in the control | Disfavored |
| Intrinsic dark-current nonuniformity | Would not normally decay from 19% asymmetry to near zero within one exposure | Strongly disfavored |
| Readout-quadrant offset | Could create spatial structure, but does not explain the smooth control-relative temporal decay | Secondary check only |
| Isolated cosmic-ray event | Would be localized and discontinuous rather than a detector-wide decaying background | Disfavored |

## Engineering interpretation

A single final fitted count-rate product compresses the temporal structure and can obscure the distinction between spatially obvious contamination and a residual common-mode tail. Rejecting only intervals that fail a spatial-symmetry test would remove the first three intervals but retain four additional intervals with measurable control-relative excess.

The result demonstrates a broader detector-characterization principle: an apparently stable spatial pattern does not prove temporal stability. Read-level temporal diagnostics and a matched control can reveal residual contamination after the most visible spatial artifact has disappeared.

## Recommended completion work

1. Sweep the common-mode threshold and report classification stability from `0.02` to `0.10 e-/s/pixel`.
2. Generate representative interval-rate maps for intervals 0, 2, 6, and 10.
3. Reprocess the affected exposure after rejecting candidate reads and compare the resulting FLT product with the archive pipeline product.
4. Quantify uncertainty from masking, border width, late-time offset window, and control-exposure selection.
5. Separate source-containing and source-free regions to test whether residual astrophysical scene differences bias the control-relative metric.

## Interpretation boundary

This analysis supports a measurement-condition diagnosis. It does not infer HgCdTe composition, carrier lifetime, dark-current mechanism, detectivity, or intrinsic material quality. The report should not be presented as evidence that the detector material itself is defective.
