# PAT-002 — Insufficient Evidence Default

## Status
Observation — not promoted to engineering

## Definition

When the extractor finds **zero or near-zero requirements**, the engine has no evidence to evaluate. Rather than surfacing this as an uncertainty signal to the user, it defaults to **BID** (because zero requirements fail → qualification score = 100/100 vacuously). The confidence score drops (e.g., 0.50), but the recommendation remains BID and the confidence value is not prominently surfaced.

This is a **decision-policy** pattern, distinct from PAT-001 (Domain Fit):
- PAT-001: engine extracts requirements but cannot detect domain mismatch
- PAT-002: engine extracts nothing; BID is the artifact of a vacuous pass, not a meaningful assessment

## Observation Log

| # | Tender | Requirements Extracted | Confidence | Engine Result | Human Result | Notes |
|---|---|---|---|---|---|---|
| 1 | Tender003 (NIT Agartala Digitization) | 0 | 0.50 | BID | NO BID | Vacuous 100/100; confidence dropped but recommendation unchanged |

## Negative Observations (Counterexamples)

Tender004 is a negative observation for PAT-002: 5 requirements were extracted, confidence = 1.0, and BID was the result. The problem in Tender004 is not insufficient evidence — it is domain-blind evaluation of sufficient (but domain-stripped) evidence. PAT-002 and PAT-001 are therefore separable: PAT-001 can occur with full confidence (Tender001, Tender002, Tender004) or low confidence (Tender003). PAT-002 specifically requires near-zero extraction AND the vacuous-pass dynamic.

| # | Tender | Requirements Extracted | Confidence | Engine Result | Notes |
|---|---|---|---|---|---|
| 1 | Tender004 (CRPF Communication Infra) | 5 | 1.00 | BID | Full evidence extracted — PAT-001 not PAT-002 |

## Observation Count
1

## Counterexample Count
1

## Appeared In
Tender003

## Bucket
C (Decision — extraction failure is Bucket B, but the unsafe default is a policy choice in the recommendation engine)

## Impact
High (1 of 1 observations) — BID on zero evidence is indistinguishable to the user from BID on complete evidence; confidence=0.50 is not surfaced in the recommendation output

## Engineering
None

## Promotion Threshold
≥ 3 independent tenders where zero or near-zero requirements are extracted and the engine still recommends BID,
AND at least 2 different tender types,
AND zero counterexamples (counterexample = engine recommends REVIEW or NO_BID when requirements are insufficient).

## Notes

**Why this is distinct from PAT-001:**
PAT-001 is about what the engine doesn't know (domain). PAT-002 is about what the engine should do when it knows it doesn't know. They can co-occur (as in Tender003) but are independent failure classes.

**The safe default question:**
When evidence is insufficient, BID is not necessarily the wrong default for every business context. Some operators may prefer to be notified (REVIEW) when confidence is below a threshold. Others may want to see BID with a visible confidence caveat. This is a product decision, not purely an engineering one — the evidence required to make it is still accumulating.

**Do not build until promotion threshold is met.**

A counterexample would be: a tender where the engine recommends REVIEW or explicitly surfaces low confidence as a reason to pause, when extraction produces zero or few requirements.
