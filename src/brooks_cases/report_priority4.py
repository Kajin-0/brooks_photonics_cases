"""Editorial de-templating and final visual hierarchy for Case 001."""

from __future__ import annotations

PRIORITY4_CSS = r'''
@page {
  @top-left {
    content: "Brooks Photonics  |  Case study 001";
    font: 500 7.4pt "IBM Plex Sans", "DejaVu Sans", sans-serif;
    color:#5D6675;
    letter-spacing:.01em;
  }
  @top-right {
    content: "WFC3/IR HgCdTe ramp integrity";
    font: 400 7.4pt "IBM Plex Sans", "DejaVu Sans", sans-serif;
    color:#667085;
  }
  @bottom-left {
    font-family:"IBM Plex Sans", "DejaVu Sans", sans-serif;
  }
  @bottom-right {
    font-family:"IBM Plex Sans", "DejaVu Sans", sans-serif;
  }
}
html,body{font-family:"IBM Plex Sans", "DejaVu Sans", sans-serif}
h1{letter-spacing:-.018em;font-weight:600}
h2,.insight-title{letter-spacing:-.008em;font-weight:600}
h3{font-weight:600}
.eyebrow,.section-tag{
  text-transform:none;
  letter-spacing:.015em;
  font-size:8.8pt;
  font-weight:500;
  color:#5E4A72;
}
.cover-accent{
  background:linear-gradient(90deg,
    #65408A 0%,
    #4D57A2 18%,
    #3478A8 35%,
    #238D8A 52%,
    #85A84B 66%,
    #D39A3B 82%,
    #BF5A3F 100%);
}
.rule{
  height:2px;
  background:linear-gradient(90deg,
    #6A3FA0 0 24%,
    #2D5F9A 24% 48%,
    #157A7A 48% 72%,
    #C35B2A 72% 100%);
  margin:8px 0 18px;
}
.metrics{grid-template-columns:1.32fr repeat(3,1fr)}
.metric{background:transparent;border-top:2px solid #6A3FA0;padding:9px 0 8px}
.metric.orange{border-color:#C35B2A}
.metric.teal{border-color:#157A7A}
.metric.blue{border-color:#2D5F9A}
.metric .value{
  font-size:19.5pt;
  font-weight:650;
  line-height:1;
  letter-spacing:-.012em;
  font-variant-numeric:tabular-nums;
}
.metric.orange .value{color:#A9461F}
.metric.teal .value{color:#126B6B}
.metric.blue .value{color:#28568A}
.metric:first-child .value{font-size:20.5pt;font-weight:700}
.metric .label{font-size:7.9pt;font-weight:500;color:#535E6F}
.card{
  border:0;
  border-top:2px solid #6A3FA0;
  padding:9px 0 7px;
  background:transparent;
}
.card.orange{border-color:#C35B2A}
.card.teal{border-color:#157A7A}
.card.blue{border-color:#2D5F9A}
.card .num{
  font-size:21.5pt;
  font-weight:700;
  line-height:.98;
  letter-spacing:-.015em;
  font-variant-numeric:tabular-nums;
  color:#6A3FA0;
}
.card.orange .num{color:#C35B2A}
.card.teal .num{color:#157A7A}
.card.blue .num{color:#2D5F9A}
.card h3{font-size:9.2pt;font-weight:600;margin-top:5px}
.banner{
  position:relative;
  background:#172033;
  color:white;
  border:0;
  border-top:3px solid #6A3FA0;
  padding:12px 14px;
}
.banner .big{color:white;font-size:14.6pt}
.banner .big span{color:#D9C6EE!important}
.banner .sub{color:#D6DCE5}
.steps{gap:11px 18px}
.step{padding-left:12px;border-left:2px solid #6A3FA0}
.step:nth-child(2){border-color:#C35B2A}
.step:nth-child(3){border-color:#157A7A}
.step:nth-child(4){border-color:#2D5F9A}
.step:before{display:none}
.commercial{
  border:0;
  border-top:2px solid #157A7A;
  border-bottom:1px solid #D9DEE6;
  background:transparent;
  padding:10px 0;
}
.commercial h3{color:#126B6B}
.figcap{
  font-size:8.1pt;
  color:#4B5667;
  line-height:1.34;
  margin-top:6px;
}
.figcap b{font-weight:650;color:#303B4B}
.result-strip{
  background:#172033;
  border:0;
  border-bottom:1px solid #172033;
  gap:1px;
}
.result-strip>div{background:#172033;color:white;padding:10px 14px}
.result-strip>div:first-child{border-top:3px solid #C35B2A}
.result-strip>div:nth-child(2){border-top:3px solid #157A7A}
.result-strip>div+div{border-left:1px solid #4A5568}
.result-strip .big{
  font-size:18.5pt;
  font-weight:700;
  letter-spacing:-.012em;
  font-variant-numeric:tabular-nums;
  color:white;
}
.result-strip>div:first-child .big{color:#F0B79C}
.result-strip>div:nth-child(2) .big{color:#A9D8D8}
.result-strip .small{color:#D4DAE4;font-weight:500}
.pill,.pill.orange,.pill.teal,.pill.gray{
  display:inline-block;
  padding:2px 5px;
  margin:0 .18em 0 0;
  border-radius:0;
  font-size:7.1pt;
  font-weight:700;
}
.pill{background:#E9DFF4;color:#4A286F}
.pill.orange{background:#F7E4DB;color:#8C3F20}
.pill.teal{background:#DCEEEE;color:#0F5E5E}
.pill.gray{background:#EDF0F4;color:#455163}
.reco:nth-of-type(1) .n{background:#6A3FA0}
.reco:nth-of-type(2) .n{background:#2D5F9A}
.reco:nth-of-type(3) .n{background:#157A7A}
.reco:nth-of-type(4) .n{background:#C35B2A}
.reco:nth-of-type(5) .n{background:#6A3FA0}
.evidence-key{display:block;border-top:1px solid #CBD2DC}
.evidence-key>div,
.evidence-key .secondary,
.evidence-key .disfavored,
.evidence-key .not-evaluated{
  display:grid;
  grid-template-columns:1.25in 1fr;
  gap:9px;
  border:0;
  border-left:3px solid #6A3FA0;
  border-bottom:1px solid #E0E4EA;
  background:transparent;
  padding:5px 0 5px 8px;
}
.evidence-key .secondary{border-left-color:#2D5F9A}
.evidence-key .disfavored{border-left-color:#A8AFBA}
.evidence-key .not-evaluated{border-left-color:#D7DBE2}
.evidence-key b{font-size:7.8pt;color:#4A286F}
.evidence-key .secondary b{color:#2D5F9A}
.evidence-key .disfavored b{color:#596273}
.evidence-key .not-evaluated b{color:#778091}
.evidence-key span{margin-top:0}
.qr-panel{
  border:0;
  border-top:2px solid #2D5F9A;
  border-bottom:1px solid #CBD2DC;
  background:white;
  padding:9px 0;
}
.cta{background:#172033;border-top:3px solid #C35B2A}
.page:nth-of-type(2) .section-tag{color:#6A3FA0}
.page:nth-of-type(3) .section-tag{color:#C35B2A}
.page:nth-of-type(4) .section-tag{color:#2D5F9A}
.page:nth-of-type(5) .section-tag{color:#157A7A}
.page:nth-of-type(6) .section-tag{color:#C35B2A}
.page:nth-of-type(7) .section-tag{color:#6A3FA0}
.page:nth-of-type(8) .section-tag{color:#157A7A}
.page:nth-of-type(9) .section-tag{color:#2D5F9A}
'''

_REPLACEMENTS = {
    "Public-data technical case study 001": "Case study 001 - public WFC3/IR data",
    "Executive conclusion and method": "Finding and method",
    "01 / Spatial evolution": "Spatial evolution",
    "02 / Temporal diagnosis and robustness": "Temporal diagnosis and robustness",
    "03 / Independent reconstruction": "Independent reconstruction",
    "04 / Engineering disposition": "Engineering disposition",
    "Technical appendix A / Method and DQ policy": "Appendix A - Method and DQ policy",
    "Technical appendix B / Complete spatial sequence": "Appendix B - Complete spatial sequence",
    "Technical appendix C / Provenance and reproducibility": "Appendix C - Provenance and reproducibility",
    "Temporal controls detect three additional affected intervals after the image appears stable": "Three affected intervals remain after visual stabilization",
    "Removing the transient materially changes the inferred count-rate product": "Excluding the transient changes the inferred count-rate product",
    "Acceptance should test temporal and spatial integrity separately": "Test temporal and spatial integrity separately",
    "The strong spatial gradient ends before the control-relative transient. A spatial-only diagnostic would stop two intervals too early.": (
        "The strong spatial gradient disappears while the control-relative transient persists. "
        "A spatial-only diagnostic would stop three intervals too early."
    ),
    "Interval-specific color scales preserve late-stage spatial detail; absolute acceptance is based on the temporal statistics reported in the client report.": (
        "Interval-specific color scales preserve late-stage spatial detail; absolute acceptance "
        "is based on the temporal statistics reported in Figure 2."
    ),
    'style="margin-top:10px;max-height:7.35in;object-fit:contain"': (
        'style="margin-top:7px;max-height:7.65in;object-fit:contain;'
        'width:104%;margin-left:-2%"'
    ),
}


def enhance_priority4_pages(pages: str) -> str:
    """Remove template-like numbering and strengthen the final editorial hierarchy."""
    for old, new in _REPLACEMENTS.items():
        pages = pages.replace(old, new)
    return pages
