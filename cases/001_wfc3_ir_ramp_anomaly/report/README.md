# Case 001 report editions

The Case 001 workflow generates two reports from the same pinned public products and derived analysis.

## Client report

`Brooks_Photonics_Case_001.pdf`

A six-page portfolio report intended for prospective customers and technical managers. It emphasizes the engineering conclusion, commercial relevance, decision robustness, reconstructed output, and recommended disposition.

## Technical report

`Brooks_Photonics_Case_001_Technical.pdf`

A nine-page companion containing the complete six-page client report plus technical appendices covering the interval-rate method, data-quality policy, full spatial sequence, file provenance, SHA-256 inventory, execution record, and references.

Both reports are generated programmatically by `src/brooks_cases/reporting.py` during `python scripts/run_case_001.py`.
