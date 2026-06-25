# PAT-005 — Structural Eligibility Condition

## Status
Candidate — 1 observation, output impact masked by PAT-003. Not promoted.

## Definition

Some tenders impose **categorical eligibility conditions** on entity type, relationship structure, or organizational form that are prerequisites to numeric threshold evaluation. These conditions cannot be expressed as numeric thresholds and have no representation in the current `Requirement` schema.

Examples of structural eligibility conditions:
- **JV / Consortium mandatory**: standalone bids categorically rejected
- **Public sector only**: private companies excluded regardless of qualifications
- **MSME category**: must hold MSME registration in specified category
- **Required authorization relationship**: OEM certification, empanelment, concession (see PAT-001 Subtype B — overlapping concept)
- **Geographic domicile**: bidder must be registered in specific state / territory
- **Equity participation floor**: bidder must hold minimum equity stake in project vehicle

The gap is at the **schema level**, not the extraction level. Even a perfect extractor cannot populate a field that does not exist in the `Requirement` model. Structural conditions cannot be reduced to `{category, threshold_value, threshold_unit}`.

**Relationship to PAT-001 Subtype B (Required Relationship):** PAT-001 Subtype B covers authorization relationships (OEM certification, dealer approval). PAT-005 covers organizational form requirements (JV mandate, entity class, equity structure). Both are structural — the distinction is whether the relationship is between bidder and a third party (PAT-001 B) or a requirement on the bidder's own organizational structure (PAT-005).

## Observation Log

| # | Tender | Authority | Condition | Engine | Human | Output Impact | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Tender010 (KRDC SH-43) | KRDC | JV mandatory — standalone bids rejected | NO_BID (experience contamination) | NO_BID (JV mandate) | Masked | PAT-003 Subtype A contaminated experience to Rs. 40 Cr; spurious FAIL drove correct output. Counterfactual without PAT-003: engine BID, human NO_BID → High impact. |

## Observation Count
1

## Counterexample Count
0

## Appeared In
Tender010

## Bucket
C (Decision) — engine cannot represent or evaluate categorical eligibility conditions. The gap is architectural: `Requirement` schema has no field for entity type, organizational form, or relationship structure conditions.

## Impact
High (latent) — confirmed at schema level in Tender010. Output-level impact masked by PAT-003 in this instance. Clean demonstration requires a tender where: (a) structural condition is the sole disqualifier, AND (b) all numeric thresholds extract correctly. If experience threshold in Tender010 had extracted correctly (Rs. 8 Crore instead of Rs. 40 Crore from contamination), engine would have recommended BID while human immediately rejects as standalone-ineligible.

## Engineering
None — candidate, not promoted.

**If promoted:** The fix requires a new requirement category and evaluation module:
- New field in `Requirement` schema: `entity_condition` (categorical, enum)
- New extractor: detect JV/consortium/entity-type language patterns
- New checker: `EntityChecker.check_single()` — evaluates company profile against entity_condition
- The check is a gate, not a score: structural ineligibility terminates evaluation before numeric thresholds

## Promotion Threshold
≥ 2 independent observations where structural eligibility condition is present AND at least 1 with confirmed output-level impact (engine recommends BID / REVIEW on a structurally ineligible tender).

**Current state:** 1 observation, output masked. Promotion blocked until output-level impact is observed.

## Notes

**On the overlap with PAT-001 Subtype B.** PAT-001 Subtype B (Required Relationship) and PAT-005 are cousins. Both are non-numeric structural conditions. The distinction: Subtype B requires a relationship to an external party (OEM, regulator, manufacturer). PAT-005 requires a specific internal organizational form (JV, public sector, MSME). Engineering treatment would differ: Subtype B requires extracting and verifying third-party authorization; PAT-005 requires extracting and matching the bidder's organizational classification.

**On RA-1 scope.** PAT-005 was surfaced by Tender010 (final RA-1 tender). One observation is insufficient for promotion. RA-1 ends with PAT-005 as a candidate, not a validated pattern. The evidence is sufficient to include "structural eligibility" as a known gap in the RA-1 Summary and as a future RA-2 test target.

**Why the third epic is weaker than the first two.** PAT-001 had 5 observations before RA-1 ended; PAT-003 had 4. PAT-005 has 1, with output masked. The RA-1 sprint was not long enough to validate a third epic. This does not mean the gap doesn't exist — the schema-level observation in Tender010 is unambiguous. It means the engineering priority is lower than the two promoted epics.
