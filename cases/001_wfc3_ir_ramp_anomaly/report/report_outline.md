# Technical report outline

## Title

**Read-Level Diagnosis of Time-Variable Contamination in a WFC3/IR HgCdTe MULTIACCUM Exposure**

## 1. Executive finding

Populate after executing the workflow:

- number and timing of flagged intervals;
- peak left-right asymmetry;
- comparison with the nominal exposure;
- effect expected from retaining contaminated reads;
- recommended read-rejection rule.

## 2. Data and provenance

- Instrument: HST WFC3/IR HgCdTe focal plane array
- Contaminated exposure: `icqtbbbxq`
- Nominal exposure: `icqtbbc0q`
- Program/visit: 14037 / BB
- Source: MAST
- Local file hashes: insert from `data/raw/inventory.json`

## 3. Method

Define cumulative charge, interval rate, masking, sigma clipping, spatial regions, normalized asymmetry, robust z-score, and anomaly criteria. State all thresholds and conduct sensitivity checks.

## 4. Results

Required figures:

1. interval median rates, contaminated versus nominal;
2. left-right asymmetry, contaminated versus nominal;
3. representative interval-rate maps;
4. sensitivity of flagged-read count to threshold;
5. optional comparison with the pipeline FLT product.

Required table:

| Metric | Contaminated | Nominal |
|---|---:|---:|
| Reads | TBD | TBD |
| Flagged intervals | TBD | TBD |
| Maximum absolute asymmetry | TBD | TBD |
| Median interval rate | TBD | TBD |

## 5. Engineering interpretation

Distinguish the following hypotheses:

- intrinsic detector dark-current or gain nonuniformity;
- stable flat-field structure;
- readout-quadrant offset;
- time-variable external background;
- isolated transient or cosmic-ray contamination.

Rank hypotheses against observed temporal and spatial signatures.

## 6. Recommended action

Specify the minimum read-level checks needed before accepting a fitted count-rate result. Quantify the exposure-time penalty caused by rejecting affected intervals and the residual spatial bias after rejection.

## 7. Limitations

The case demonstrates ramp-integrity diagnosis using calibrated public data. It is not a material-qualification study and does not infer intrinsic HgCdTe composition, lifetime, or detectivity.
