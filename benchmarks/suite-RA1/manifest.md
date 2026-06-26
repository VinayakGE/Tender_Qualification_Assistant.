# Suite RA-1 — Manifest

**Created:** 2026-06-25 (RA-1 sprint)
**Tenders:** 10
**Company profile:** `examples/Tender-001/company-profile.json` (Apex Infrastructure Pvt Ltd — road contractor, Karnataka)
**Profile fixed at:** 2026-06-25 — do not modify

## Company Profile Summary (Apex Infrastructure Pvt Ltd)

| Field | Value |
|---|---|
| Company ID | APEX-INFRA-001 |
| Sector | Road construction (all 3 completed projects) |
| Annual turnover | Rs. 42.3 / 38.1 / 51.2 Crore (3-year) |
| Net worth | Rs. 18.4 Crore |
| Certifications | ISO 9001:2015, ISO 14001:2015 |
| Registered class | Class-I PWD Contractor, Karnataka |

## Tender Manifest

| ID | File | Authority | Work Type | Contract Value | Human Verdict | Human Primary Reason |
|---|---|---|---|---|---|---|
| T01 | Tender001.pdf | CRPF | Defence BOP building construction | ~Rs. 9.5 Crore | NO_BID | Domain mismatch (defence building) |
| T02 | Tender002.pdf | NIT Nagaland | Lift AMC (Otis-specific) | ~Rs. 0.8 Crore | NO_BID | Domain mismatch + OEM requirement |
| T03 | Tender003.pdf | NIT Calicut | Library digitization | ~Rs. 1.2 Crore | NO_BID | Domain mismatch (IT digitization) |
| T04 | Tender004.pdf | CRPF | Communications infrastructure | ~Rs. 4.5 Crore | NO_BID | Domain mismatch (communications) |
| T05 | Tender005.pdf | BBMP | Road resurfacing, Bangalore | ~Rs. 3.2 Crore | BID | Domain match + thresholds pass |
| T06 | Tender006.pdf | NHAI | Highway widening, 4-laning | ~Rs. 85 Crore | NO_BID | Threshold fail (turnover Rs. 85 Crore > Apex 43.87) |
| T07 | Tender007.pdf | CNNL | Canal desilting, irrigation | ~Rs. 12 Crore | NO_BID | Domain mismatch (irrigation/canal) |
| T08 | Tender008.pdf | CPWD/KVS | Institutional building construction | ~Rs. 11.8 Crore | NO_BID | Domain mismatch (building) |
| T09 | Tender009.pdf | RVNL | Road over bridge (ROB) | ~Rs. 18.5 Crore | NO_BID | Domain mismatch (railway/bridge) |
| T10 | Tender010.pdf | KRDC | Highway widening SH-43 (JV mandatory) | ~Rs. 35 Crore | NO_BID | JV mandatory (standalone ineligible) |

## Human Verdict Distribution

| Verdict | Count | Tenders |
|---|---|---|
| BID | 1 | T05 |
| NO_BID | 9 | T01–T04, T06–T10 |

## Notes

- T05 and T06 are **positive controls**: T05 must remain BID (domain match + pass), T06 must remain NO_BID via threshold.
- T10 human NO_BID is due to JV mandate (PAT-005), not thresholds. Engine may agree on output but disagree on reason — count as output agreement, reasoning disagreement until PAT-005 implemented.
- Human verdicts are fixed and will not be revised retrospectively.
