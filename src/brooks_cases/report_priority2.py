"""Priority-2 document-control, QR, and PDF metadata refinements."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import qrcode

CASE_URL = (
    "https://github.com/Kajin-0/brooks_photonics_cases/"
    "tree/main/cases/001_wfc3_ir_ramp_anomaly"
)
REPORT_REVISION_DEFAULT = "1.4"

PRIORITY2_CSS = r'''
.document-control{text-align:right;color:#566173;font-size:7.5pt;line-height:1.25}
.document-control .doc-id{font-size:9.2pt;font-weight:750;color:#172033;letter-spacing:.035em}
.qr-panel{display:grid;grid-template-columns:0.82in 1fr;gap:11px;align-items:center;border:1px solid #DDE2EA;border-radius:0;padding:8px 10px;margin-top:10px;background:#FAFBFC}
.qr-panel img{width:.76in;height:.76in;image-rendering:crisp-edges}.qr-panel h3{margin-bottom:2px}.qr-panel p{font-size:7.35pt;color:#566173;margin-bottom:2px;line-height:1.27}.qr-panel .contact{font-size:7.35pt;font-weight:700;color:#172033;margin-top:4px;white-space:nowrap}
.doc-control-table td:first-child{width:39%}
'''


def build_repository_qr(destination: Path) -> Path:
    """Create a compact, print-safe QR code for the Case 001 technical package."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(CASE_URL)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#172033", back_color="white")
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)
    return destination


def _build_date_utc() -> str:
    explicit = os.environ.get("REPORT_BUILD_DATE_UTC")
    if explicit:
        return explicit
    return datetime.now(timezone.utc).date().isoformat()


def add_priority2_context(context: dict[str, object], *, technical: bool) -> None:
    """Add report revision and document-control fields."""
    context["document_control"] = {
        "document_id": "BP-CS-001-T" if technical else "BP-CS-001-C",
        "revision": os.environ.get("REPORT_REVISION", REPORT_REVISION_DEFAULT),
        "build_date_utc": _build_date_utc(),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID", "local build"),
        "edition": "Technical report" if technical else "Client report",
    }


def metadata_head(context: dict[str, object], *, technical: bool) -> str:
    """Return HTML metadata that WeasyPrint maps into the PDF information dictionary."""
    control = context["document_control"]
    edition = "Technical" if technical else "Client"
    title = f"Brooks Photonics Case 001 - {edition} Report"
    subject = (
        "Read-level diagnosis of a time-variable background transient in public "
        "HST WFC3/IR HgCdTe detector data."
    )
    keywords = (
        "Brooks Photonics, HgCdTe, WFC3/IR, infrared detector, ramp analysis, "
        "time-variable background, detector characterization, reproducible analysis"
    )
    return (
        f"<title>{title}</title>"
        '<meta name="author" content="Brooks Photonics">'
        f'<meta name="description" content="{subject}">'
        f'<meta name="keywords" content="{keywords}">'
        '<meta name="generator" content="Brooks Photonics Cases 0.1.0 / WeasyPrint">'
        f'<meta name="dcterms.created" content="{control["build_date_utc"]}">'
        f'<meta name="dcterms.modified" content="{control["build_date_utc"]}">'
    )


def enhance_priority2_pages(
    pages: str,
    context: dict[str, object],
    assets: dict[str, str],
    *,
    technical: bool,
) -> str:
    """Insert document control and the technical-package QR panel."""
    control = context["document_control"]
    cover_control = (
        '<div class="document-control">'
        f'<div class="doc-id">{control["document_id"]}</div>'
        f'<div>Rev {control["revision"]} &middot; {control["build_date_utc"]}</div>'
        "</div>"
    )
    pages = pages.replace('<div class="date">July 2026</div>', cover_control, 1)

    if not technical:
        return pages

    execution_marker = '<tr><td>Python package</td><td>brooks-photonics-cases 0.1.0</td></tr>'
    execution_rows = (
        f'<tr><td>Document identifier</td><td class="mono">{control["document_id"]}</td></tr>'
        f'<tr><td>Report revision</td><td>Rev {control["revision"]}</td></tr>'
        f'<tr><td>Build date</td><td>{control["build_date_utc"]} UTC</td></tr>'
        f'<tr><td>Workflow run</td><td class="mono">{control["workflow_run_id"]}</td></tr>'
        + execution_marker
    )
    pages = pages.replace(execution_marker, execution_rows, 1)

    original_cta = (
        '<div class="cta" style="margin-top:17px"><h3>Brooks Photonics</h3>'
        '<p>Independent, physics-based analysis of infrared detector electrical, '
        'spectral, temporal, and noise data.</p>'
        '<div class="contact">brooks-photonics.com &nbsp; | &nbsp; '
        'terence@brooks-photonics.com</div></div>'
    )
    combined_panel = (
        '<div class="qr-panel">'
        f'<a href="{CASE_URL}" style="text-decoration:none">'
        f'<img src="{assets["repository_qr"]}" alt="QR code for the Case 001 repository">'
        "</a>"
        '<div><h3>Open the reproducible technical package</h3>'
        '<p>Scan or select the code for the source, pinned manifest, derived tables, '
        'figures, tests, and report workflow.</p>'
        '<p><b>Brooks Photonics:</b> independent, physics-based analysis of infrared '
        'detector electrical, spectral, temporal, and noise data.</p>'
        '<div class="contact">brooks-photonics.com &nbsp; | &nbsp; '
        'terence@brooks-photonics.com</div></div></div>'
    )
    pages = pages.replace(original_cta, combined_panel, 1)
    return pages
