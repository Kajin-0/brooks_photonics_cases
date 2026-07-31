# Sources and provenance

## Public measurements

The FITS products are public Hubble Space Telescope WFC3/IR data distributed by the Mikulski Archive for Space Telescopes (MAST). Exact product URIs and filenames are pinned in `data/manifest.csv`. Local byte counts and SHA-256 digests are written to `data/raw/inventory.json` after download.

Case 001 uses:

- `icqtbbbxq_ima.fits` — affected nondestructive-read ramp;
- `icqtbbc0q_ima.fits` — nominal comparison ramp;
- `icqtbbbxq_flt.fits` — archived fitted count-rate product for the affected ramp;
- `icqtbbc0q_flt.fits` — archived fitted count-rate product for the nominal ramp.

## Official technical references

1. STScI, **WFC3/IR IMA Visualization Tools with an Example of Time Variable Background**. Identifies `icqtbbbxq` as strongly contaminated by scattered light and `icqtbbc0q` as the nominal comparison exposure.
2. STScI, **Correcting for Scattered Light in WFC3/IR Exposures: Manually Subtracting Bad Reads**. Documents program 14037, visit BB, and the affected exposure.
3. STScI, **WFC3 Data Handbook — WFC3 File Structure**. Documents IMA science, error, data-quality, sample, and time extensions and their storage order.
4. STScI, **WFC3 Data Handbook — IR Data Calibration Steps**. Documents read-by-read calibration and up-the-ramp processing.
5. STScI, **WFC3 Data Handbook — WFC3 Data Quality Flags**. Documents `DATAREJECT=8192` as a sample rejected during up-the-ramp fitting rather than a permanent detector defect.

Links:

- https://spacetelescope.github.io/hst_notebooks/notebooks/WFC3/ir_ima_visualization/IR_IMA_Visualization_with_an_Example_of_Time_Variable_Background.html
- https://spacetelescope.github.io/hst_notebooks/notebooks/WFC3/ir_scattered_light_manual_corrections/Correcting_for_Scattered_Light_in_IR_Exposures_by_Manually_Subtracting_Bad_Reads.html
- https://hst-docs.stsci.edu/wfc3dhb/chapter-2-wfc3-data-structure/2-2-wfc3-file-structure
- https://hst-docs.stsci.edu/wfc3dhb/chapter-3-wfc3-data-calibration/3-3-ir-data-calibration-steps
- https://hst-docs.stsci.edu/wfc3dhb/chapter-7-wfc3-data-quality/7-10-wfc3-data-quality-flags
- https://mast.stsci.edu/api/v0/

## Analysis attribution

> Analysis by Brooks Photonics using public HST WFC3/IR measurements obtained from MAST. HST data and official calibration documentation are credited to NASA, ESA, and STScI. Brooks Photonics is not affiliated with or endorsed by those organizations.

## Interpretation boundary

Official STScI documentation establishes the data provenance, file semantics, and known time-variable-background context. All numerical metrics, thresholds, source masking, spatial bootstrap results, and independent ramp reconstructions in this repository are Brooks Photonics analyses unless explicitly stated otherwise.
