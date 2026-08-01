"""Priority-1 editorial refinements for the Case 001 reports."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def add_priority1_context(case_dir: Path, context: dict[str, object]) -> None:
    """Add a data-derived explanation for the nominal transient threshold."""
    table = pd.read_csv(case_dir / "data" / "derived" / "exposure_comparison.csv")
    late_intervals = int(context["summary"]["analysis_settings"]["late_intervals"])
    threshold = float(
        context["summary"]["analysis_settings"]["common_mode_threshold_e_s"]
    )
    late_residuals = table["transient_excess_e_s"].tail(late_intervals).to_numpy(float)
    late_median = float(np.median(late_residuals))
    robust_scale = float(1.4826 * np.median(np.abs(late_residuals - late_median)))
    context["threshold_rationale"] = {
        "threshold_e_s": threshold,
        "late_intervals": late_intervals,
        "late_residual_median_e_s": late_median,
        "late_residual_scale_e_s": robust_scale,
        "threshold_multiple": threshold / robust_scale,
    }


def enhance_priority1_pages(pages: str, context: dict[str, object]) -> str:
    """Apply the Priority-1 narrative, threshold, direction, and citation refinements."""
    rationale = context["threshold_rationale"]
    threshold = rationale["threshold_e_s"]
    scale = rationale["late_residual_scale_e_s"]
    multiple = rationale["threshold_multiple"]
    rate_unit = "electrons s<sup>-1</sup> pixel<sup>-1</sup>"

    contribution_note = """
      <div class="side-note" style="margin-top:10px"><b>Source distinction.</b> STScI documents the affected/control exposure pair, the Earth-limb scattered-light interpretation, and the read-level visualization example. Brooks Photonics independently adds spatial-versus-common-mode endpoint separation, source-mask and threshold sensitivity tests, block-bootstrap uncertainty, and quantitative post-transient refitting.</div>
"""
    page_two_marker = """      </ul></div>
    </div>
  </div>
</section>

<section class=\"page\">
  <div class=\"section-tag\">01 / Spatial evolution</div>"""
    page_two_replacement = """      </ul></div>
%s    </div>
  </div>
</section>

<section class=\"page\">
  <div class=\"section-tag\">01 / Spatial evolution</div>""" % contribution_note
    pages = pages.replace(page_two_marker, page_two_replacement, 1)

    original_caption = (
        f'<div class="figcap"><b>Figure 2.</b> Intervals 0 to 6 exceed the nominal '
        f'0.05 <span class="unit">{rate_unit}</span> common-mode threshold after '
        "matched-control subtraction and late-offset removal.</div>"
    )
    revised_caption = (
        f'<div class="figcap"><b>Figure 2.</b> Intervals 0 to 6 exceed the nominal '
        f'{threshold:.2f} <span class="unit">{rate_unit}</span> limit after '
        "matched-control subtraction and late-offset removal. The limit is "
        f"{multiple:.2f} times the robust late-ramp residual scale "
        f"({scale:.5f} <span class=\"unit\">{rate_unit}</span>) and is not an "
        "official WFC3 pipeline threshold.</div>"
    )
    pages = pages.replace(original_caption, revised_caption)

    pages = pages.replace(
        f"Median change in {rate_unit}",
        f"Lower than archived FLT in {rate_unit}",
    )

    original_boundary = (
        f"The 0.05 <span class=\"unit\">{rate_unit}</span> threshold is a transparent "
        "engineering criterion for this demonstration, not an official WFC3 pipeline threshold."
    )
    revised_boundary = (
        f"The {threshold:.2f} <span class=\"unit\">{rate_unit}</span> threshold was "
        f"selected before the sensitivity sweep at {multiple:.2f} times the robust "
        f"late-ramp residual scale ({scale:.5f} <span class=\"unit\">{rate_unit}</span>). "
        "It is a transparent engineering operating limit, not an official WFC3 pipeline threshold."
    )
    pages = pages.replace(original_boundary, revised_boundary)

    client_references = {
        "[1] Space Telescope Science Institute, <i>WFC3/IR IMA Visualization Tools with an Example of Time Variable Background</i>, technical notebook.": (
            "[1] O’Connor, A., Khandrika, H., Mack, J., and Calamida, A. (2023), "
            "<i>WFC3/IR IMA Visualization Tools with an Example of Time Variable Background</i>, "
            "HST/WFC3 Notebooks, updated 2023-05-05."
        ),
        "[2] Space Telescope Science Institute, <i>WFC3 Data Handbook</i>, file-structure and IR-calibration sections.": (
            "[2] Pagul, A., Rivera, I., et al. (2024), <i>WFC3 Data Handbook</i>, "
            "Version 6.0, Space Telescope Science Institute."
        ),
        "[3] Mikulski Archive for Space Telescopes, public HST product archive and download API.": (
            "[3] Mikulski Archive for Space Telescopes (MAST), HST public product archive "
            "and download API; products retrieved for Case 001 in 2026."
        ),
    }
    for old, new in client_references.items():
        pages = pages.replace(old, new)

    technical_references = {
        "[1] Space Telescope Science Institute. <i>WFC3/IR IMA Visualization Tools with an Example of Time Variable Background</i>. HST technical notebook.": (
            "[1] O’Connor, A., Khandrika, H., Mack, J., and Calamida, A. (2023). "
            "<i>WFC3/IR IMA Visualization Tools with an Example of Time Variable Background</i>. "
            "HST/WFC3 Notebooks; updated 2023-05-05."
        ),
        "[2] Space Telescope Science Institute. <i>Correcting for Scattered Light in WFC3/IR Exposures: Manually Subtracting Bad Reads</i>. HST technical notebook.": (
            "[2] O’Connor, A., Mack, J., Calamida, A., and Khandrika, H. (2023). "
            "<i>Correcting for Scattered Light in WFC3/IR Exposures: Manually Subtracting Bad Reads</i>. "
            "HST/WFC3 Notebooks; updated 2023-11-13."
        ),
        "[3] Space Telescope Science Institute. <i>WFC3 Data Handbook</i>. Sections on WFC3 file structure and IR calibration.": (
            "[3] Pagul, A., Rivera, I., et al. (2024). <i>WFC3 Data Handbook</i>, "
            "Version 6.0. Baltimore: Space Telescope Science Institute."
        ),
        "[4] Space Telescope Science Institute. <i>WFC3 Instrument Handbook</i>. IR detector characteristics and readout.": (
            "[4] Marinelli, M., and Green, J. (2025). <i>Wide Field Camera 3 Instrument Handbook</i>, "
            "Version 18.0. Baltimore: Space Telescope Science Institute."
        ),
        "[5] Mikulski Archive for Space Telescopes. HST public product archive and download API.": (
            "[5] Mikulski Archive for Space Telescopes (MAST). HST public product archive "
            "and download API; products and persistent product identifiers listed in the provenance table."
        ),
    }
    for old, new in technical_references.items():
        pages = pages.replace(old, new)

    return pages
