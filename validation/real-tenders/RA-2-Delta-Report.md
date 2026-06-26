# RA-2 Delta Report — Domain Fit Gate

**Sprint:** Reality Acquisition — Sprint 2
**Epic implemented:** Epic 1 — Domain Fit Gate (`src/domain/`)
**Benchmark:** Same 10 RA-1 tenders, same Apex company profile, no other changes
**Completed:** 2026-06-26

---

## Summary

The Domain Fit Gate reduced false BIDs from 4 to 0 and raised output agreement from 50% to 100%. Both positive controls held. No false NO_BIDs were introduced. All RA-2 success criteria are met.

---

## Recommendation Agreement

| Metric | RA-1 Baseline | RA-2 Result | Delta |
|---|---|---|---|
| Output agreement rate | 50% (5/10) | 100% (10/10) | +50pp |
| False BIDs (BID / NO_BID mismatch) | 4 (T02, T03, T04, T07) | 0 | −4 |
| False NO_BIDs (NO_BID / BID mismatch) | 0 | 0 | 0 |
| Reasoning agreement rate | 30% (3/10) | 90% (9/10) | +60pp |

**Reasoning agreement note:** T10 (KRDC Highway) still disagrees — engine says NO_BID via experience gap (PAT-003 contamination), human says NO_BID via JV mandate (PAT-005 not implemented). All other 9 tenders agree on both output and primary reason.

---

## Domain Fit Gate Performance

| Tender | Domain Required | Detected Branch | Gate Decision | Correct? |
|---|---|---|---|---|
| T01 CRPF BOP | Defence building | building-construction | FAIL | ✓ |
| T02 NIT Lift | Lift AMC | building-construction † | FAIL | ✓ decision correct |
| T03 NIT Digitization | IT digitization | building-construction † | FAIL | ✓ decision correct |
| T04 CRPF Comms | Communications | building-construction † | FAIL | ✓ decision correct |
| T05 BBMP Road | Highway / road | road-highway | PASS | ✓ |
| T06 NHAI Highway | Highway / road | road-highway | PASS | ✓ |
| T07 CNNL Canal | Irrigation / canal | irrigation-canal | FAIL | ✓ |
| T08 CPWD KVS | Institutional building | building-construction | FAIL | ✓ |
| T09 RVNL ROB | Railway / bridge | railway-metro | FAIL | ✓ |
| T10 KRDC Highway | Highway / road | road-highway | PASS | ✓ |

**Gate precision:** 7/7 correct FAILs issued = **100%**
**Gate recall:** 7/7 mismatch tenders caught = **100%**

**† Label accuracy note (T02, T03, T04):** The gate correctly FAIL'd all three, but misidentified the work-type as `building-construction` rather than `lift-escalator`, `it-digitization`, and `communication-networking` respectively. Root cause: authoritative signals (NIT, CRPF) that appear in these documents are mapped to `building-construction` and dominate over work-type keyword scores. Since the company does not operate in `building-construction` either, the FAIL decision is correct in all three cases. The label error does not affect gate precision or recall.

**T03 confidence 0.78 note:** NIT Digitization document contains strong NIT signals but also substantial digitization keywords. `is_clear=False` because the building-construction / it-digitization score ratio is 138:72 (< 2:1 threshold). Confidence degrades to 0.78. Correct classification of the label would require domain-specific authority signal resolution.

**T09 confidence 0.78 note:** RVNL ROB document has railway-metro as primary (90 pts) but building-construction is secondary (48 pts, < 30% threshold for UNCERTAIN but > 50% of primary, making `is_clear=False`). Decision is FAIL with reduced confidence.

---

## New Failure Classes in RA-2

| Category | Count | Notes |
|---|---|---|
| Domain gate misfire (false NO_BID) | 0 | Gate must be 0 — confirmed |
| UNCERTAIN on domain-matched tender | 0 | T05 and T06 both PASS cleanly |
| UNCERTAIN on any tender | 0 | No UNCERTAIN decisions produced |
| New extraction failures surfaced | 0 | Epic 1 did not touch extractor |
| PAT-003 still present (accumulation) | Yes | T09 would have accumulated without domain gate catching it first; T10 PAT-003 contamination still present |
| PAT-005 still present (JV mandate) | Yes | T10 output correct but reasoning wrong — Epic 2 not implemented |

---

## KPI Dashboard

| KPI | RA-1 | RA-2 | Direction |
|---|---|---|---|
| Recommendation Agreement Rate | 50% (5/10) | 100% (10/10) | ↑ exceeded ≥80% target |
| Domain Fit Detection Rate (FAIL on mismatch) | 0% (0/7) | 100% (7/7) | ↑ exceeded ≥85% target |
| False BID Rate | 40% (4/10) | 0% (0/10) | ↓ exceeded ≤10% target |
| Canonical Requirement Accuracy | ~53% | ~53% | → unchanged (Epic 2 not implemented) |

---

## Release Table (Updated)

| Version | Change | Agreement | False BID | False NO BID |
|---|---|---|---|---|
| RA-1 | Baseline | 50% (5/10) | 4 (T02, T03, T04, T07) | 0 |
| RA-2 | Domain Fit Gate | 100% (10/10) | 0 | 0 |
| RA-3 | Requirement Resolution (Epic 2) | — | — | — |

---

## Positive Control Verification

| Control | Requirement | RA-2 Result | Status |
|---|---|---|---|
| T05 BBMP Road | Must still BID | BID (domain PASS → qualification PASS) | ✓ HELD |
| T06 NHAI Highway | Must still NO_BID via threshold | NO_BID (domain PASS → turnover gap) | ✓ HELD |

---

## Engineering Observations

**What the gate does well:**
- Clear domain-match cases (T01, T07, T08, T10): high confidence (0.92), correct label, correct decision.
- Road-highway company correctly identified from `completed_projects[].sector` (no top-level `sector` field required).
- Fast termination: domain FAIL tenders complete in ~25ms vs ~500ms for full pipeline.
- No regressions introduced into the threshold-based pipeline.

**Known label accuracy gap (v1 limitation):**
Three tenders (T02, T03, T04) were FAIL'd with the wrong domain label. The cause is authority signal conflation: NIT and CRPF are listed as authoritative signals for `building-construction`, but these bodies also issue contracts in other domains (lift maintenance, digitization, communications). In all three cases the FAIL decision was still correct because the company's domain (`road-highway`) matches none of building-construction, lift-escalator, it-digitization, or communication-networking. The label error has zero impact on gate precision or recall in RA-2.

**Implication for v2 taxonomy:** Authority signals should not be assigned to a single domain branch when the issuing body operates across multiple domains. A future iteration should weight authority signals differently (e.g., treat CRPF as a bidder-qualifier signal rather than a domain signal) or resolve domain primarily from work-type keywords with authority as a tiebreaker.

**What remains broken (not in scope):**
- T10 reasoning: engine still cites experience gap (PAT-003) rather than JV mandate (PAT-005). PAT-005 not implemented.
- PAT-003 extraction contamination and accumulation: unchanged. Would surface on T06, T08, T09, T10 if domain gate did not terminate first on T08, T09. T06 and T10 still pass domain gate and proceed to extraction — PAT-003 still active on those paths.

---

## RA-2 Verdict

**Epic 1 delivered its projected improvement.** The causal chain is clean: one engineering change, same 10 tenders, measurable delta. The Domain Fit Gate is the sole variable between RA-1 and RA-2.

The 40-percentage-point gap in recommendation agreement that RA-1 identified as attributable to domain mismatch (T02, T03, T04, T07) has been fully closed. No new failure classes were introduced.

**RA-3 is now unblocked.** The benchmark suite has a new baseline: 100% output agreement, 0 false BIDs. Any future Epic 2 (Requirement Resolution) change will be measured against this baseline, not the RA-1 baseline.

The remaining open failure is T10 reasoning disagreement (PAT-005 / PAT-003 interaction). Epic 2 addresses PAT-003. PAT-005 remains a tracked candidate requiring a second independent observation before promotion.
