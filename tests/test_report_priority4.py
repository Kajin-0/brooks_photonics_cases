from __future__ import annotations

from brooks_cases.report_priority4 import PRIORITY4_CSS, enhance_priority4_pages


def test_editorial_layer_removes_template_numbering() -> None:
    pages = (
        "Public-data technical case study 001 "
        "01 / Spatial evolution "
        "02 / Temporal diagnosis and robustness "
        "03 / Independent reconstruction "
        "04 / Engineering disposition "
        "Technical appendix A / Method and DQ policy"
    )
    enhanced = enhance_priority4_pages(pages)
    assert "01 /" not in enhanced
    assert "02 /" not in enhanced
    assert "03 /" not in enhanced
    assert "04 /" not in enhanced
    assert "Case study 001 - public WFC3/IR data" in enhanced
    assert "Appendix A - Method and DQ policy" in enhanced


def test_editorial_css_uses_institutional_typography_and_reduces_ui_tropes() -> None:
    assert "IBM Plex Sans" in PRIORITY4_CSS
    assert ".cover-accent{background:#6A3FA0}" in PRIORITY4_CSS
    assert ".pill,.pill.orange" in PRIORITY4_CSS
    assert "background:none" in PRIORITY4_CSS
    assert ".step:before{display:none}" in PRIORITY4_CSS
