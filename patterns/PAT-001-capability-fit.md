# PAT-001 — Capability Fit

## Status
Observation — not promoted to engineering

## Definition

A bidder's **work-type capability** does not match the tender's **required work type**, but the pipeline's eligibility checker passes the bidder because it evaluates thresholds (value, count) only — not semantic work-type compatibility.

Examples of work types that are distinct and currently indistinguishable by the engine:
- Road construction / highway
- Building construction (residential, institutional, defence)
- Irrigation / dam / waterway
- Electrical / power transmission
- Rail / metro
- Telecom / IT infrastructure
- HVAC / MEP

## Observation Log

| # | Tender | Sector Required | Company Sector | Engine Result | Human Result | Impact |
|---|---|---|---|---|---|---|
| 1 | Tender001 (CRPF BOP Rajasthan) | Building construction (defence) | Road construction | BID (pass) | REVIEW | High |
| 2 | Tender002 (NIT Agartala Otis Lift AMC) | Lift AMC / OEM-authorized service | Road construction | BID (pass) | NO BID | High |

## Observation Count
2

## Counterexample Count
0

## Appeared In
Tender001, Tender002

## Bucket
B (Extraction — sector type not captured in any requirement field)

## Impact
High (2 of 2 observations) — wrong BID recommendation on tenders the company cannot qualify for; Tender002 is a NO BID (hard disqualifier via OEM certificate), stronger failure than Tender001's REVIEW

## Engineering
None

## Promotion Threshold
≥ 3 independent tenders showing capability-fit mismatch with High impact, zero counterexamples

## Notes

This pattern sits at the B/C boundary:
- **Bucket B root cause**: the `Requirement` schema has no `work_type` or `sector` field; extraction cannot record what type of work the experience must be in
- **Bucket C consequence**: the eligibility checker has no logic to compare company sector profile against requirement sector; it passes on value alone

A counterexample would be: a tender where the engine correctly identifies a capability-fit match/mismatch without sector-type fields (e.g., because the company profile sector happens to be checked by some other mechanism).

**Do not build until promotion threshold is met.**
