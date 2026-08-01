"""Professional client and technical portfolio report generation for Case 001."""

from __future__ import annotations

import json
import os
from pathlib import Path

from weasyprint import HTML

from brooks_cases.advanced import flt_reconstruction_metrics, make_source_free_mask
from brooks_cases.client_spatial import plot_client_spatial_sequence
from brooks_cases.report_assets import _build_report_hero, _load_context
from brooks_cases.report_map_figures import (
    plot_flt_reconstruction_maps,
    plot_full_spatial_sequence,
)
from brooks_cases.report_priority1 import add_priority1_context, enhance_priority1_pages
from brooks_cases.report_priority2 import (
    PRIORITY2_CSS,
    add_priority2_context,
    build_repository_qr,
    enhance_priority2_pages,
    metadata_head,
)
from brooks_cases.report_templates import _client_pages, _technical_appendix
from brooks_cases.report_theme import REPORT_CSS
from brooks_cases.wfc3 import load_flt, load_ima

REPOSITORY_URL = "https://github.com/Kajin-0/brooks_photonics_cases"
WEBSITE_URL = "https://brooks-photonics.com/"
CONTACT_EMAIL = "terence@brooks-photonics.com"

LINK_CSS = r'''
a{color:#4A286F;text-decoration:underline;text-decoration-thickness:.6px;text-underline-offset:1.5px}
.sources a{color:#354760}.cta a{color:white;text-decoration:none}.contact-link{white-space:nowrap}
'''


def _resolve_source_sha() -> str:
    """Resolve the actual source-head SHA instead of a temporary PR merge SHA."""
    explicit = os.environ.get("ANALYSIS_SOURCE_SHA")
    if explicit:
        return explicit
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if event_path:
        try:
            event = json.loads(Path(event_path).read_text(encoding="utf-8"))
            pull_request = event.get("pull_request")
            if pull_request:
                head_sha = pull_request.get("head", {}).get("sha")
                if head_sha:
                    return str(head_sha)
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    return os.environ.get("GITHUB_SHA", "repository history")


def _prepare_report_figures(case_dir: Path, context: dict[str, object]) -> None:
    """Generate all report-visible maps directly from the source arrays."""
    raw = case_dir / "data" / "raw"
    figures = case_dir / "figures"
    affected = load_ima(raw / "icqtbbbxq_ima.fits")
    control = load_ima(raw / "icqtbbc0q_ima.fits")

    plot_client_spatial_sequence(
        affected,
        control,
        figures / "client_spatial_sequence.png",
    )
    plot_full_spatial_sequence(
        affected,
        control,
        figures / "representative_interval_maps.png",
    )

    source_result = make_source_free_mask(control)
    common_mode_intervals = context["comparison"]["common_mode_flagged_intervals"]
    clean_start_positive_read = (
        max(common_mode_intervals) + 1 if common_mode_intervals else 0
    )
    affected_flt = load_flt(raw / "icqtbbbxq_flt.fits")
    _, flt_maps = flt_reconstruction_metrics(
        affected,
        affected_flt,
        source_result.analysis_mask,
        clean_start_positive_read=clean_start_positive_read,
    )
    plot_flt_reconstruction_maps(
        flt_maps,
        figures / "flt_reconstruction.png",
    )


def _linkify(pages: str) -> str:
    """Add live website, email, repository, and reference annotations."""
    contact = (
        f'<a class="contact-link" href="{WEBSITE_URL}">brooks-photonics.com</a>'
        " &nbsp; | &nbsp; "
        f'<a class="contact-link" href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>'
    )
    pages = pages.replace(
        "brooks-photonics.com &nbsp; | &nbsp; terence@brooks-photonics.com",
        contact,
    )
    pages = pages.replace(
        "Raw FITS files remain outside Git; the repository stores exact URIs, "
        "derived tables, figures, tests, and the complete execution workflow.",
        "Raw FITS files remain outside Git; the repository stores exact URIs, "
        "derived tables, figures, tests, and the complete execution workflow. "
        f'<a href="{REPOSITORY_URL}">Open the repository and reproducibility package.</a>',
    )
    pages = pages.replace(
        "The complete case can be regenerated from four pinned public products.",
        "The complete case can be regenerated from four pinned public products. "
        f'<a href="{REPOSITORY_URL}">Open the source repository.</a>',
    )

    references = {
        "WFC3/IR IMA Visualization Tools with an Example of Time Variable Background": (
            "https://spacetelescope.github.io/hst_notebooks/notebooks/WFC3/"
            "ir_ima_visualization/"
            "IR_IMA_Visualization_with_an_Example_of_Time_Variable_Background.html"
        ),
        "Correcting for Scattered Light in WFC3/IR Exposures: Manually Subtracting Bad Reads": (
            "https://spacetelescope.github.io/hst_notebooks/notebooks/WFC3/"
            "ir_scattered_light_manual_corrections/"
            "Correcting_for_Scattered_Light_in_IR_Exposures_by_Manually_Subtracting_Bad_Reads.html"
        ),
        "WFC3 Data Handbook": "https://hst-docs.stsci.edu/wfc3dhb",
        "WFC3 Instrument Handbook": "https://hst-docs.stsci.edu/wfc3ihb",
        "Wide Field Camera 3 Instrument Handbook": "https://hst-docs.stsci.edu/wfc3ihb",
    }
    for title, url in references.items():
        pages = pages.replace(
            f"<i>{title}</i>",
            f'<a href="{url}"><i>{title}</i></a>',
        )
    pages = pages.replace(
        "Mikulski Archive for Space Telescopes",
        '<a href="https://archive.stsci.edu/">Mikulski Archive for Space Telescopes</a>',
    )
    return pages


def _build_report(
    case_dir: Path,
    output_path: Path,
    *,
    technical: bool,
    context: dict[str, object],
) -> None:
    report_context = dict(context)
    add_priority2_context(report_context, technical=technical)

    figures = case_dir / "figures"
    report_assets = case_dir / "report" / "_assets"
    report_assets.mkdir(parents=True, exist_ok=True)
    hero_path = _build_report_hero(
        figures / "representative_interval_maps.png",
        report_assets / "report_hero.png",
    )
    qr_path = build_repository_qr(report_assets / "case_001_repository_qr.png")
    assets = {
        "hero": hero_path.resolve().as_uri(),
        "client_spatial": (figures / "client_spatial_sequence.png").resolve().as_uri(),
        "temporal": (figures / "temporal_diagnosis.png").resolve().as_uri(),
        "robustness": (figures / "robustness_summary.png").resolve().as_uri(),
        "flt": (figures / "flt_reconstruction.png").resolve().as_uri(),
        "spatial_dq": (figures / "spatial_and_dq.png").resolve().as_uri(),
        "full_spatial": (figures / "representative_interval_maps.png").resolve().as_uri(),
        "repository_qr": qr_path.resolve().as_uri(),
    }
    pages = _client_pages(report_context, assets)
    if technical:
        os.environ["GITHUB_SHA"] = _resolve_source_sha()
        pages += _technical_appendix(report_context, assets)
    pages = enhance_priority1_pages(pages, report_context)
    pages = enhance_priority2_pages(
        pages,
        report_context,
        assets,
        technical=technical,
    )
    pages = _linkify(pages)
    html_document = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        + metadata_head(report_context, technical=technical)
        + "<style>"
        + REPORT_CSS
        + LINK_CSS
        + PRIORITY2_CSS
        + "</style></head><body>"
        + pages
        + "</body></html>"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_document, base_url=str(case_dir.resolve())).write_pdf(output_path)


def build_case_001_report(case_dir: Path, output_path: Path) -> None:
    """Build the client report and its technical companion."""
    context = _load_context(case_dir)
    add_priority1_context(case_dir, context)
    _prepare_report_figures(case_dir, context)
    _build_report(case_dir, output_path, technical=False, context=context)
    technical_path = output_path.with_name(f"{output_path.stem}_Technical.pdf")
    _build_report(case_dir, technical_path, technical=True, context=context)


def build_case_001_technical_report(case_dir: Path, output_path: Path) -> None:
    """Build the nine-page technical version with method and provenance appendices."""
    context = _load_context(case_dir)
    add_priority1_context(case_dir, context)
    _prepare_report_figures(case_dir, context)
    _build_report(case_dir, output_path, technical=True, context=context)
