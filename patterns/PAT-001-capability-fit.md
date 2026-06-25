# PAT-001 — Capability Fit

## Status
Observation — **promotion threshold met** (pending RA-1 Summary completion before any Type 2 engineering change)

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
- Lift / escalator AMC
- IT / digitization services

## Observation Log

| # | Tender | Sector Required | Company Sector | Engine Result | Human Result | Impact |
|---|---|---|---|---|---|---|
| 1 | Tender001 (CRPF BOP Rajasthan) | Building construction (defence) | Road construction | BID (pass) | REVIEW | High |
| 2 | Tender002 (NIT Agartala Otis Lift AMC) | Lift AMC / OEM-authorized service | Road construction | BID (pass) | NO BID | High |
| 3 | Tender003 (NIT Agartala Digitization) | IT services / document digitization | Road construction | BID (pass, 0.50 confidence) | NO BID | High |

## Observation Count
3

## Counterexample Count
0

## Appeared In
Tender001, Tender002, Tender003

## Bucket
B (Extraction — sector type not captured in any requirement field)

## Impact
High (3 of 3 observations) — wrong BID recommendation on all three tenders; all would result in immediate disqualification or wasted bid preparation; Tender002 and Tender003 are outright NO BID (OEM certificate and IT experience are hard disqualifiers respectively)

## Engineering
None

## Promotion Threshold
≥ 3 independent tenders showing capability-fit mismatch with High impact,
AND at least 2 different sectors,
AND at least 2 different issuing authorities,
AND zero counterexamples.

**Threshold met as of Tender003:** 3 tenders, 3 sectors (building construction; lift AMC; IT digitization), 2 authorities (CRPF; NIT Agartala), 0 counterexamples. Engineering change blocked by RA-1 sprint freeze — no Type 2 change until RA-1-Summary.md is complete.

## Candidate Subtypes

Tender002 introduced a variant not present in Tender001. The pattern may have at least two subtypes. **Do not split into separate patterns yet — one more observation needed to confirm whether these are the same failure class or distinct.**

**Subtype A — Capability Fit (work type)**
The bidder's completed work portfolio is in a different construction/service domain than the tender requires. Engine passes on value threshold alone.
- Example: road contractor evaluated on building construction tender.

**Subtype B — Required Relationship**
The tender requires a formal authorization relationship between the bidder and a third party (manufacturer, OEM, regulator), not merely capability or experience. No threshold value exists to extract; the requirement is structural.
- Examples: OEM authorization, dealer certification, manufacturer approval, technology partnership, empanelment on approved vendor list.
- Tender002 (Otis OEM certificate) is the first observation.

Both subtypes share the same root cause: the `Requirement` schema has no field to encode authorization relationships or work-type constraints, so extraction cannot record them and the eligibility checker cannot evaluate them.

## Notes

This pattern sits at the B/C boundary:
- **Bucket B root cause**: the `Requirement` schema has no `work_type`, `sector`, or `authorization_relationship` field; extraction cannot record what type of work or what authorization the experience must demonstrate
- **Bucket C consequence**: the eligibility checker has no logic to compare company sector profile against requirement sector, or to verify authorization relationships; it passes on value alone

A counterexample would be: a tender where the engine correctly identifies a capability-fit match/mismatch without sector-type fields (e.g., because the company profile sector happens to be checked by some other mechanism).

**Do not build until promotion threshold is met.**
