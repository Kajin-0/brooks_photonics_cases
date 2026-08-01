from __future__ import annotations

from brooks_cases.report_priority2 import (
    CASE_URL,
    add_priority2_context,
    build_repository_qr,
    enhance_priority2_pages,
    metadata_head,
)


def test_document_control_and_metadata(monkeypatch) -> None:
    monkeypatch.setenv("REPORT_BUILD_DATE_UTC", "2026-08-01")
    monkeypatch.setenv("REPORT_REVISION", "1.2")
    monkeypatch.setenv("GITHUB_RUN_ID", "123456")
    context: dict[str, object] = {}
    add_priority2_context(context, technical=True)

    control = context["document_control"]
    assert control["document_id"] == "BP-CS-001-T"
    assert control["revision"] == "1.2"
    assert control["build_date_utc"] == "2026-08-01"
    assert control["workflow_run_id"] == "123456"

    head = metadata_head(context, technical=True)
    assert "Brooks Photonics Case 001 - Technical Report" in head
    assert 'name="author" content="Brooks Photonics"' in head
    assert 'name="keywords"' in head
    assert 'dcterms.created" content="2026-08-01"' in head


def test_priority2_page_enhancement_adds_controls_and_qr(monkeypatch) -> None:
    monkeypatch.setenv("REPORT_BUILD_DATE_UTC", "2026-08-01")
    context: dict[str, object] = {}
    add_priority2_context(context, technical=True)
    pages = (
        '<div class="date">July 2026</div>'
        '<table><tr><td>Python package</td><td>brooks-photonics-cases 0.1.0</td></tr></table>'
        '<div class="cta" style="margin-top:17px"><h3>Brooks Photonics</h3>'
        '<p>Independent, physics-based analysis of infrared detector electrical, '
        'spectral, temporal, and noise data.</p>'
        '<div class="contact">brooks-photonics.com &nbsp; | &nbsp; '
        'terence@brooks-photonics.com</div></div>'
    )
    enhanced = enhance_priority2_pages(
        pages,
        context,
        {"repository_qr": "file:///tmp/qr.png"},
        technical=True,
    )
    assert "BP-CS-001-T" in enhanced
    assert "Rev 1.2" in enhanced
    assert "2026-08-01" in enhanced
    assert CASE_URL in enhanced
    assert "file:///tmp/qr.png" in enhanced
    assert "Open the reproducible technical package" in enhanced
    assert "independent, physics-based analysis" in enhanced


def test_repository_qr_is_written(tmp_path) -> None:
    output = build_repository_qr(tmp_path / "case_qr.png")
    assert output.exists()
    assert output.stat().st_size > 500
