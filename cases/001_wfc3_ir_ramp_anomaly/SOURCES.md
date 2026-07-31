# Sources and provenance

## Public measurements

The FITS products are public Hubble Space Telescope WFC3/IR data distributed by the Mikulski Archive for Space Telescopes (MAST). Exact product URIs and filenames are pinned in `data/manifest.csv`.

## Official technical references

1. STScI, **WFC3/IR IMA Visualization Tools with an Example of Time Variable Background**. This official notebook identifies `icqtbbbxq` as strongly contaminated by scattered light and `icqtbbc0q` as the nominal comparison exposure.
2. STScI, **Correcting for Scattered Light in WFC3/IR Exposures: Manually Subtracting Bad Reads**. This official notebook documents program 14037, visit BB, and the affected exposure.
3. STScI, **WFC3 Data Handbook — WFC3 File Structure**. Documents the IMA science, error, data-quality, sample, and time extensions and reverse chronological storage.
4. STScI, **WFC3 Data Handbook — IR Data Calibration Steps**. Documents read-by-read calibration and up-the-ramp processing.

Links:

- https://spacetelescope.github.io/hst_notebooks/notebooks/WFC3/ir_ima_visualization/IR_IMA_Visualization_with_an_Example_of_Time_Variable_Background.html
- https://spacetelescope.github.io/hst_notebooks/notebooks/WFC3/ir_scattered_light_manual_corrections/Correcting_for_Scattered_Light_in_IR_Exposures_by_Manually_Subtracting_Bad_Reads.html
- https://hst-docs.stsci.edu/wfc3dhb/chapter-2-wfc3-data-structure/2-2-wfc3-file-structure
- https://hst-docs.stsci.edu/wfc3dhb/chapter-3-wfc3-data-calibration/3-3-ir-data-calibration-steps
- https://mast.stsci.edu/api/v0/

## Attribution statement for reports

> Analysis by Brooks Photonics using public HST WFC3/IR measurements obtained from MAST. HST data and official calibration documentation are credited to NASA, ESA, and STScI. Brooks Photonics is not affiliated with or endorsed by those organizations.
