# PAT-001 — Domain Fit

## Status
Observation — **promotion threshold met** (pending RA-1 Summary completion before any Type 2 engineering change)

## Definition

A bidder's **commercial domain** does not match the tender's **required domain**, but the pipeline's eligibility checker passes the bidder because it evaluates thresholds (value, count) only — not semantic domain compatibility.

"Domain" is broader than "capability." It encompasses:
- Work-type portfolio (what the company has built or delivered)
- Industry identity (what sector the company operates in)
- Authorization relationships (OEM certification, empanelment, licensing that are structurally required, not merely experiential)

A road contractor is not just incapable of Lift AMC work — they inhabit a different commercial domain. That distinction precedes all threshold evaluation.

Examples of domains that are distinct and currently indistinguishable by the engine:
- Road construction / highway
- Building construction (residential, institutional, defence)
- Irrigation / dam / waterway
- Electrical / power transmission
- Rail / metro
- Telecom / IT infrastructure
- HVAC / MEP
- Lift / escalator AMC
- IT / digitization services
- Facility management / housekeeping
- Security services

## Observation Log

| # | Tender | Domain Required | Company Domain | Engine Result | Human Result | Impact |
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
B (Extraction — domain type not captured in any requirement field)

## Impact
High (3 of 3 observations) — wrong BID recommendation on all three tenders; all would result in immediate disqualification or wasted bid preparation; Tender002 and Tender003 are outright NO BID (OEM certificate and IT experience are structural disqualifiers that no threshold check can catch)

## Engineering
None

## Promotion Threshold
≥ 3 independent tenders showing domain-fit mismatch with High impact,
AND at least 2 different sectors,
AND at least 2 different issuing authorities,
AND zero counterexamples.

**Threshold met as of Tender003:** 3 tenders, 3 sectors (building construction; lift AMC; IT digitization), 2 authorities (CRPF; NIT Agartala), 0 counterexamples. Engineering change blocked by RA-1 sprint freeze — no Type 2 change until RA-1-Summary.md is complete.

## Candidate Subtypes

Both subtypes share the same root cause but manifest differently. Promote as a single pattern — the split exists for engineering precision later.

**Subtype A — Work-Type Domain Mismatch**
The bidder's completed work portfolio is in a different sector than the tender requires. Engine passes on value threshold alone.
- Example: road contractor evaluated on building construction tender (Tender001), IT digitization tender (Tender003).

**Subtype B — Required Relationship**
The tender requires a formal authorization relationship between the bidder and a third party (manufacturer, OEM, regulator). No threshold value exists to extract; the requirement is structural and non-numeric.
- Examples: OEM authorization, dealer certification, manufacturer approval, technology partnership, empanelment on approved vendor list.
- Tender002 (Otis OEM certificate) is the first and only observation.

## Notes

This pattern sits at the B/C boundary:
- **Bucket B root cause**: the `Requirement` schema has no `domain`, `work_type`, `sector`, or `authorization_relationship` field; extraction cannot record what domain the experience must be in or what authorization is structurally required
- **Bucket C consequence**: the eligibility checker has no logic to compare company domain against requirement domain, or to detect that authorization relationships cannot be satisfied; it passes on value alone

**On the product-level implication:** Domain Fit is not a feature to be added to the existing pipeline — it is a prerequisite gate that runs before threshold evaluation. The current pipeline sequence (extract → check thresholds → score → recommend) assumes domain fit; it never tests it. See `docs/OFE-candidate.md` for the candidate architecture that addresses this structural gap.

A counterexample would be: a tender where the engine correctly identifies a domain-fit match or mismatch without explicit domain fields (e.g., because some other mechanism in the company profile is checked against the tender).

**Engineering change requires RA-1-Summary.md completion before implementation.**
