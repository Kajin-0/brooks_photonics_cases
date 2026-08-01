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
.rule{height:1px;background:#BCA9CE;margin:8px 0 18px}
.metrics{grid-template-columns:1.32fr repeat(3,1fr)}
.metric{background:transparent;border-top:2px solid #6A3FA0;padding:9px 0 8px}
.metric.orange{border-color:#C35B2A}
.metric.teal,.metric.blue{border-color:#6A3FA0}
.metric .value{
  font-size:19.5pt;
  font-weight:650;
  line-height:1;
  letter-spacing:-.012em;
  font-variant-numeric:tabular-nums;
}
.metric:first-child .value{font-size:20.5pt;font-weight:700}
.metric .label{font-size:7.9pt;font-weight:500;color:#535E6F}
.card{
  border:0;
  border-top:1px solid #CBD2DC;
  padding:9px 0 7px;
  background:transparent;
}
.card .num{
  font-size:21.5pt;
  font-weight:700;
  line-height:.98;
  letter-spacing:-.015em;
  font-variant-numeric:tabular-nums;
}
.card h3{font-size:9.2pt;font-weight:600;margin-top:5px}
.card.teal .num,.card.blue .num{color:#172033}
.banner{
  background:#F4F2F6;
  color:#172033;
  border-left:3px solid #6A3FA0;
  padding:12px 14px;
}
.banner .big{color:#172033;font-size:14.6pt}
.banner .big span{color:#4A286F!important}
.banner .sub{color:#4F5A6B}
.steps{gap:11px 18px}
.step{padding-left:12px;border-left:2px solid #BCA9CE}
.step:before{display:none}
.commercial{
  border:0;
  border-top:1px solid #BCA9CE;
  border-bottom:1px solid #D9DEE6;
  background:transparent;
  padding:10px 0;
}
.figcap{
  font-size:8.1pt;
  color:#4B5667;
  line-height:1.34;
  margin-top:6px;
}
.figcap b{font-weight:650;color:#303B4B}
.result-strip{
  background:transparent;
  border-top:1px solid #9FA8B7;
  border-bottom:1px solid #9FA8B7;
  gap:0;
}
.result-strip>div{background:white;color:#172033;padding:10px 14px}
.result-strip>div+div{border-left:1px solid #CDD3DD}
.result-strip .big{
  font-size:18.5pt;
  font-weight:700;
  letter-spacing:-.012em;
  font-variant-numeric:tabular-nums;
}
.result-strip .small{color:#5C6676;font-weight:500}
.pill,.pill.orange,.pill.teal,.pill.gray{
  display:inline;
  padding:0;
  margin:0 .18em 0 0;
  background:none;
  color:#172033;
  font-size:inherit;
  font-weight:650;
}
.evidence-key{display:block;border-top:1px solid #CBD2DC}
.evidence-key>div,
.evidence-key .secondary,
.evidence-key .disfavored,
.evidence-key .not-evaluated{
  display:grid;
  grid-template-columns:1.25in 1fr;
  gap:9px;
  border:0;
  border-bottom:1px solid #E0E4EA;
  background:transparent;
  padding:5px 0;
}
.evidence-key b{font-size:7.8pt}
.evidence-key span{margin-top:0}
.qr-panel{
  border:0;
  border-top:1px solid #CBD2DC;
  border-bottom:1px solid #CBD2DC;
  background:white;
  padding:9px 0;
}
.cta{background:#172033}
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
