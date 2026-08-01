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


def test_editorial_css_uses_institutional_typography_and_multicolor_accents() -> None:
    assert "IBM Plex Sans" in PRIORITY4_CSS
    assert ".cover-accent{" in PRIORITY4_CSS
    assert "linear-gradient" in PRIORITY4_CSS
    assert "#65408A" in PRIORITY4_CSS
    assert ".metric.teal{border-color:#157A7A}" in PRIORITY4_CSS
    assert ".metric.blue{border-color:#2D5F9A}" in PRIORITY4_CSS
    assert ".card.orange .num{color:#C35B2A}" in PRIORITY4_CSS
    assert ".card.teal .num{color:#157A7A}" in PRIORITY4_CSS
    assert ".card.blue .num{color:#2D5F9A}" in PRIORITY4_CSS
    assert ".step:nth-child(2){border-color:#C35B2A}" in PRIORITY4_CSS
    assert ".step:before{display:none}" in PRIORITY4_CSS


def test_multicolor_accents_preserve_square_geometry() -> None:
    assert ".pill,.pill.orange" in PRIORITY4_CSS
    assert "border-radius:0" in PRIORITY4_CSS
    assert ".pill.orange{background:#F7E4DB" in PRIORITY4_CSS
    assert ".pill.teal{background:#DCEEEE" in PRIORITY4_CSS
    assert ".result-strip>div:first-child{border-top:3px solid #C35B2A}" in PRIORITY4_CSS
    assert ".result-strip>div:nth-child(2){border-top:3px solid #157A7A}" in PRIORITY4_CSS


def test_final_hierarchy_strengthens_metrics_captions_and_results() -> None:
    assert ".card .num{" in PRIORITY4_CSS
    assert "font-size:21.5pt" in PRIORITY4_CSS
    assert ".figcap{" in PRIORITY4_CSS
    assert "font-size:8.1pt" in PRIORITY4_CSS
    assert ".result-strip .big{" in PRIORITY4_CSS
    assert "font-weight:700" in PRIORITY4_CSS


def test_spatial_figure_is_enlarged_without_restoring_section_numbers() -> None:
    pages = (
        '<div class="section-tag">01 / Spatial evolution</div>'
        '<img class="figure" style="margin-top:10px;max-height:7.35in;object-fit:contain">'
    )
    enhanced = enhance_priority4_pages(pages)
    assert "01 /" not in enhanced
    assert "max-height:7.65in" in enhanced
    assert "width:104%" in enhanced
