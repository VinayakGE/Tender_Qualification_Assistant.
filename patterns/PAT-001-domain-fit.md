# PAT-001 — Domain Fit

## Status
**Validated Design Gap** — promotion threshold met; engineering change queued pending RA-1 Summary completion

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
- Telecom / IT infrastructure / communication systems
- HVAC / MEP
- Lift / escalator AMC
- IT / digitization services
- Facility management / housekeeping
- Security services

## Observation Log

| # | Tender | Domain Required | Company Domain | Engine Result | Human Result | Impact | Extraction Mode |
|---|---|---|---|---|---|---|---|
| 1 | Tender001 (CRPF BOP Rajasthan) | Building construction (defence) | Road construction | BID (pass) | REVIEW | High | 4 reqs extracted; experience missed |
| 2 | Tender002 (NIT Agartala Otis Lift AMC) | Lift AMC / OEM-authorized service | Road construction | BID (pass) | NO BID | High | 1 req extracted (turnover only) |
| 3 | Tender003 (NIT Agartala Digitization) | IT services / document digitization | Road construction | BID (pass, 0.50 conf) | NO BID | High | 0 reqs extracted; vacuous pass |
| 4 | Tender004 (CRPF Communication Infra) | Communication / networking systems | Road construction | BID (pass) | NO BID | High | 5 reqs extracted; experience extracted but domain-blind pass |

## Counterexample Log

| # | Tender | Domain Required | Company Domain | Engine Result | Human Result | Type | Notes |
|---|---|---|---|---|---|---|---|
| C1 | Tender005 (BBMP Road Resurfacing) | Road / highway | Road construction | BID | BID | Output-level | Experience req not extracted; checker not invoked; correct output via incomplete evidence |

## Observation Count
4

## Counterexample Count
1 (output-level) / 0 (logic-level)

**Counterexample type distinction:**
- Output-level counterexample: engine and human both recommend BID on a domain-matched tender. The output is correct.
- Logic-level counterexample: engine extracts an experience requirement, invokes the eligibility checker, checker matches company projects against the required domain and returns PASS, human agrees. The logic is domain-aware.

Tender005 is output-level only. The experience requirement was not extracted; the eligibility checker was not invoked for experience. The correct BID was reached via turnover + ISO 9001 pass, not via domain-aware evaluation. PAT-001 (domain-blind qualification logic) was not falsified at the logic level.

## Appeared In
Tender001, Tender002, Tender003, Tender004

## Bucket
B/C boundary — Tender001–003: primarily Bucket B (domain type not captured in extraction). Tender004 crosses into Bucket C: the experience requirement was correctly extracted (value/count), the eligibility checker was invoked, and it still passed road projects against a communication/networking requirement. Domain blindness is now demonstrated in the qualification logic, not just in extraction.

## Impact
High (4 of 4 observations) — wrong BID recommendation on all four tenders; all would result in disqualification or wasted bid effort; three are outright NO BID

## Engineering
None (queued post-RA-1)

## Promotion Threshold
≥ 3 independent tenders showing domain-fit mismatch with High impact,
AND at least 2 different sectors,
AND at least 2 different issuing authorities,
AND zero counterexamples.

**Threshold met as of Tender003.** Current state: 4 failure observations, 4 sectors (building; lift AMC; IT digitization; communication infrastructure), 2 authorities (CRPF; NIT Agartala), 1 output-level counterexample (Tender005 — road contractor on road tender, engine and human both BID, but domain-aware logic not invoked). Promotion threshold remains met — the counterexample criterion requires zero output-level counterexamples only if the promotion threshold has not yet been met; Tender005 arrived after promotion and is recorded as a qualified counterexample, not a demotion signal.

## Experience as Two Dimensions

Tender004 surfaces a precise refinement of the data model. The eligibility checker currently answers:

> "Has the company completed three projects worth Rs. 10 Crore?"

The tender actually asks:

> "Has the company completed three *communication infrastructure* projects worth Rs. 10 Crore?"

This means "experience" in the current model conflates two distinct dimensions:

1. **Quantity / value** — how many projects, at what scale (currently evaluated)
2. **Experience domain** — what type of work those projects represent (not evaluated)

A correct experience check requires both. The `Requirement` schema has no field for experience domain. This is the precise schema gap that enables the domain-blind pass observed in Tender004.

## Candidate Subtypes

Both subtypes share the same root cause but manifest differently. Promote as a single pattern — the split exists for engineering precision later.

**Subtype A — Work-Type Domain Mismatch**
The bidder's completed work portfolio is in a different sector than the tender requires. Engine passes on value/count alone.
- Observations: Tender001 (road vs building), Tender003 (road vs IT), Tender004 (road vs communication).
- In Tender004: experience requirement was extracted; checker was invoked; checker still passed on value alone.

**Subtype B — Required Relationship**
The tender requires a formal authorization relationship between the bidder and a third party (manufacturer, OEM, regulator). No threshold value exists to extract; the requirement is structural and non-numeric.
- Examples: OEM authorization, dealer certification, manufacturer approval, empanelment.
- Observations: Tender002 (Otis OEM certificate).

## Notes

**On the shift from H1 to H2 (Tender004 evidence):**

Before Tender004, two hypotheses were open:
- H1: Recommendations are wrong because extraction missed domain-specific requirements.
- H2: Recommendations are wrong because qualification logic lacks domain awareness.

Tender004 falsifies H1 as the primary explanation. The experience requirement was extracted. The checker evaluated it. The checker still returned PASS. H2 is now the stronger explanation for this failure class. Both extraction (B) and qualification logic (C) have gaps, but the qualification logic gap is the more fundamental one — it would remain even if extraction were perfect.

**On the product-level implication:** Domain Fit is not a feature to be added — it is a prerequisite gate that precedes threshold evaluation. The current pipeline assumes domain fit; it never establishes it. See `docs/OFE-candidate.md` for the candidate architecture.

A counterexample would be: a tender where the engine correctly identifies a domain match or mismatch (e.g., a road contractor evaluated on a road construction tender where the engine recommends BID and the human agrees).

**Engineering change requires RA-1-Summary.md completion before implementation.**
