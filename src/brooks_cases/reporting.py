"""Professional client and technical portfolio report generation for Case 001."""

from __future__ import annotations

from pathlib import Path

from weasyprint import HTML

from brooks_cases.report_assets import (
    _build_client_spatial_figure,
    _build_report_hero,
    _load_context,
)
from brooks_cases.report_templates import _client_pages, _technical_appendix
from brooks_cases.report_theme import REPORT_CSS


def _build_report(case_dir: Path, output_path: Path, *, technical: bool) -> None:
    figures = case_dir / "figures"
    report_assets = case_dir / "report" / "_assets"
    report_assets.mkdir(parents=True, exist_ok=True)
    context = _load_context(case_dir)
    hero_path = _build_report_hero(
        figures / "representative_interval_maps.png",
        report_assets / "report_hero.png",
    )
    client_spatial = _build_client_spatial_figure(
        figures / "representative_interval_maps.png",
        report_assets / "client_spatial_sequence.png",
    )
    assets = {
        "hero": hero_path.resolve().as_uri(),
        "client_spatial": client_spatial.resolve().as_uri(),
        "temporal": (figures / "temporal_diagnosis.png").resolve().as_uri(),
        "robustness": (figures / "robustness_summary.png").resolve().as_uri(),
        "flt": (figures / "flt_reconstruction.png").resolve().as_uri(),
        "spatial_dq": (figures / "spatial_and_dq.png").resolve().as_uri(),
        "full_spatial": (figures / "representative_interval_maps.png").resolve().as_uri(),
    }
    pages = _client_pages(context, assets)
    if technical:
        pages += _technical_appendix(context, assets)
    html_document = (
        "<!doctype html><html><head><meta charset='utf-8'><style>"
        + REPORT_CSS
        + "</style></head><body>"
        + pages
        + "</body></html>"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_document, base_url=str(case_dir.resolve())).write_pdf(output_path)


def build_case_001_report(case_dir: Path, output_path: Path) -> None:
    """Build the client report and its technical companion."""
    _build_report(case_dir, output_path, technical=False)
    technical_path = output_path.with_name(f"{output_path.stem}_Technical.pdf")
    _build_report(case_dir, technical_path, technical=True)


def build_case_001_technical_report(case_dir: Path, output_path: Path) -> None:
    """Build the nine-page technical version with method and provenance appendices."""
    _build_report(case_dir, output_path, technical=True)
