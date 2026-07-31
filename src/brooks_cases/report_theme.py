"""Shared visual system for Case 001 reports."""

REPORT_CSS = r'''
@page { size: Letter; margin: 0.56in 0.62in 0.53in 0.62in;
  @top-left { content: "BROOKS PHOTONICS  /  CASE STUDY 001"; font: 600 7.3pt "Liberation Sans"; color:#6A3FA0; letter-spacing:.08em; }
  @top-right { content: "WFC3/IR HgCdTe ramp integrity"; font: 400 7.3pt "Liberation Sans"; color:#667085; }
  @bottom-left { content: "Independent physics-based infrared detector analysis"; font: 400 6.9pt "Liberation Sans"; color:#687386; }
  @bottom-right { content: counter(page); font: 600 7.3pt "Liberation Sans"; color:#556070; }
}
@page:first { @top-left { content:none } @top-right { content:none } @bottom-left { content:none } }
*{box-sizing:border-box} html{font-family:"Liberation Sans",Arial,sans-serif;color:#172033;font-size:10.2pt;line-height:1.42}
body{margin:0} .page{break-after:page; min-height:9.15in; position:relative} .page:last-child{break-after:auto}
h1,h2,h3,p{margin-top:0} h1{font-size:29pt;line-height:1.03;letter-spacing:-.035em;margin-bottom:14px;max-width:6.9in}
h2{font-size:20pt;line-height:1.12;letter-spacing:-.025em;margin-bottom:12px} h3{font-size:11.8pt;line-height:1.25;margin-bottom:6px}
.eyebrow{font-size:8.3pt;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:#6A3FA0;margin-bottom:13px}
.deck{font-size:12.6pt;line-height:1.38;color:#495467;max-width:6.55in;margin-bottom:17px}
.rule{height:3px;background:linear-gradient(90deg,#6A3FA0 0 18%,#D8C7E9 18% 100%);margin:7px 0 18px}
.hero{width:100%;height:2.08in;object-fit:cover;object-position:center top;border-radius:4px;display:block}
.cover-meta{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;margin-top:14px}.cover-meta .small{font-size:8.2pt;color:#667085}.date{font-size:9.2pt;font-weight:700;color:#6A3FA0}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin:14px 0 18px}.metric{border-top:3px solid #6A3FA0;background:#F7F5FA;padding:9px 10px 10px;min-height:.72in}.metric.orange{border-color:#C35B2A}.metric.teal{border-color:#157A7A}.metric.blue{border-color:#2D5F9A}.metric .value{font-size:17pt;font-weight:750;letter-spacing:-.03em;line-height:1.05}.metric .label{font-size:7.6pt;color:#5D6778;margin-top:4px;line-height:1.22}
.section-tag{font-size:7.4pt;font-weight:700;letter-spacing:.12em;color:#6A3FA0;text-transform:uppercase;margin-bottom:6px}.lead{font-size:11.1pt;line-height:1.46;color:#344054;max-width:6.85in}
.callout{border-left:4px solid #6A3FA0;background:#F5F1F8;padding:12px 15px;margin:12px 0 15px;font-size:11.4pt;font-weight:650;line-height:1.36}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}
.card{border:1px solid #DDE2EA;border-radius:4px;padding:12px;background:white}.card h3{color:#243044}.card p{font-size:8.9pt;color:#4D5869;margin-bottom:0}.card .num{font-size:18pt;font-weight:750;color:#6A3FA0;margin-bottom:3px}.card.orange .num{color:#C35B2A}.card.teal .num{color:#157A7A}.card.blue .num{color:#2D5F9A}
.figure{width:100%;display:block}.figcap{font-size:7.6pt;color:#5F6B7D;line-height:1.35;margin-top:6px}.insight-title{font-size:17.3pt;line-height:1.18;letter-spacing:-.02em;max-width:6.75in;margin-bottom:11px}
.side-note{font-size:8.2pt;color:#5F6B7D;border-top:1px solid #CBD2DC;padding-top:7px}
.kpi-table{width:100%;border-collapse:collapse;margin-top:10px;font-size:8.4pt}.kpi-table th{background:#EFF2F6;text-align:left;padding:6px 7px;font-size:7.3pt;text-transform:uppercase;letter-spacing:.05em;color:#4E596A}.kpi-table td{padding:6px 7px;border-bottom:1px solid #E2E6EC;vertical-align:top}.kpi-table td:last-child{font-weight:650;color:#202A3A}.kpi-table tr:last-child td{border-bottom:0}
.steps{counter-reset:steps;display:grid;grid-template-columns:1fr 1fr;gap:9px 16px;margin-top:11px}.step{position:relative;padding-left:32px;min-height:40px;font-size:8.7pt;color:#495467}.step:before{counter-increment:steps;content:counter(steps);position:absolute;left:0;top:0;width:23px;height:23px;border-radius:50%;background:#6A3FA0;color:#fff;text-align:center;line-height:23px;font-weight:700;font-size:8.2pt}
.banner{background:#172033;color:white;padding:15px 17px;border-radius:4px;margin:12px 0}.banner .big{font-size:15.5pt;font-weight:700;line-height:1.24}.banner .sub{font-size:8.6pt;color:#D6DCE5;margin-top:6px}
.pill{display:inline-block;border-radius:999px;padding:3px 7px;background:#E9DFF4;color:#4A286F;font-weight:700;font-size:7.2pt;margin-right:4px}.pill.orange{background:#F7E4DB;color:#8C3F20}.pill.teal{background:#DCEEEE;color:#0F5E5E}.pill.gray{background:#EDF0F4;color:#455163}
.reco{display:grid;grid-template-columns:30px 1fr;gap:9px;margin:8px 0}.reco .n{width:26px;height:26px;background:#6A3FA0;color:white;border-radius:4px;text-align:center;line-height:26px;font-weight:700}.reco h3{margin-bottom:1px}.reco p{font-size:8.8pt;color:#4D5869;margin-bottom:0}
.sources{font-size:7.4pt;color:#4F5B6D;line-height:1.36}.cover-accent{position:absolute;top:-.56in;right:-.62in;width:2.7in;height:.17in;background:linear-gradient(90deg,#6A3FA0,#C35B2A,#157A7A)}
.result-strip{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#CFD6E1;border-radius:4px;overflow:hidden;margin:10px 0 12px}.result-strip>div{background:#172033;color:white;padding:12px 15px}.result-strip .big{font-size:17pt;font-weight:750;line-height:1.05}.result-strip .small{font-size:7.8pt;color:#D4DAE4;margin-top:4px}
.commercial{border:1px solid #D9CBE7;background:#FBF9FD;padding:12px 14px;border-radius:4px}.commercial ul{margin:5px 0 0 17px;padding:0}.commercial li{font-size:8.8pt;color:#425066;margin:4px 0}
.evidence-key{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin:8px 0}.evidence-key>div{border-top:3px solid #6A3FA0;background:#F7F5FA;padding:7px}.evidence-key b{font-size:7.8pt}.evidence-key span{display:block;font-size:6.9pt;color:#667085;margin-top:2px;line-height:1.22}.evidence-key .secondary{border-color:#2D5F9A}.evidence-key .disfavored{border-color:#A8AFBA}.evidence-key .not-evaluated{border-color:#D7DBE2}
.cta{background:#172033;color:white;border-radius:4px;padding:17px 19px}.cta h3{font-size:14.5pt;color:white;margin-bottom:6px}.cta p{font-size:8.8pt;color:#D8DEE8;margin-bottom:4px}.cta .contact{font-size:9.5pt;font-weight:700;color:white;margin-top:9px}
.eq{background:#F6F7F9;border-left:3px solid #6A3FA0;padding:8px 11px;margin:8px 0;font-family:"Liberation Serif",serif;font-size:11pt}.unit{white-space:nowrap}.mono{font-family:"Liberation Mono",monospace;font-size:7.2pt}
.provenance{font-size:7.1pt}.provenance td:first-child{font-family:"Liberation Mono",monospace}.nowrap{white-space:nowrap}
'''
