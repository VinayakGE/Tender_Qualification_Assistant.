# Suite RA-1 — Results After RA-2 (Domain Fit Gate)

**Run date:** 2026-06-26
**Pipeline version:** RA-2 (Domain Fit Gate implemented)
**Domain Fit Gate:** Active — `src/domain/` (DomainExtractor → DomainMatcher → DomainFitGate)
**Change from RA-1:** One change only: Stage 1.5 Domain Fit Gate inserted before extraction

## Per-Tender Results

| Tender | Human Verdict | Engine Verdict | Output Agreement | Gate Decision | Detected Branch | Gate Correct? | Engine Primary Reason | Reasoning Agreement |
|---|---|---|---|---|---|---|---|---|
| T01 CRPF BOP | NO_BID | NO_BID | ✓ | FAIL | building-construction | ✓ label ✓ | Domain Mismatch | ✓ |
| T02 NIT Lift | NO_BID | NO_BID | ✓ | FAIL | building-construction † | ✓ decision | Domain Mismatch | ✓ |
| T03 NIT Digitization | NO_BID | NO_BID | ✓ | FAIL | building-construction † | ✓ decision | Domain Mismatch | ✓ |
| T04 CRPF Comms | NO_BID | NO_BID | ✓ | FAIL | building-construction † | ✓ decision | Domain Mismatch | ✓ |
| T05 BBMP Road | BID | BID | ✓ | PASS | road-highway | ✓ | Qualification pass | ✓ |
| T06 NHAI Highway | NO_BID | NO_BID | ✓ | PASS | road-highway | ✓ | Turnover threshold fail | ✓ |
| T07 CNNL Canal | NO_BID | NO_BID | ✓ | FAIL | irrigation-canal | ✓ label ✓ | Domain Mismatch | ✓ |
| T08 CPWD KVS | NO_BID | NO_BID | ✓ | FAIL | building-construction | ✓ label ✓ | Domain Mismatch | ✓ |
| T09 RVNL ROB | NO_BID | NO_BID | ✓ | FAIL | railway-metro | ✓ label ✓ | Domain Mismatch | ✓ |
| T10 KRDC Highway | NO_BID | NO_BID | ✓ | PASS | road-highway | ✓ | Experience gap (PAT-003) | ✗ (JV mandate, PAT-005) |

**†** Label accuracy note: T02, T03, T04 detected as `building-construction` rather than `lift-escalator`, `it-digitization`, `communication-networking` respectively. Authority signals (NIT, CRPF) drove the label. FAIL decision is correct in all three cases. See RA-2-Delta-Report.md §Engineering Observations.

## Aggregate Metrics

| Metric | RA-1 | RA-2 | Delta |
|---|---|---|---|
| Output agreement | 5/10 = 50% | **10/10 = 100%** | +50pp |
| False BIDs | 4 | **0** | −4 |
| False NO_BIDs | 0 | **0** | 0 |
| Reasoning agreement | 3/10 = 30% | **9/10 = 90%** | +60pp |
| Domain Fit detection rate (FAIL on mismatch) | 0% | **100% (7/7)** | +100pp |
| Gate precision | n/a | **100% (7/7)** | — |
| Gate recall | n/a | **100% (7/7)** | — |

## Positive Control Verification

| Control | Requirement | Result | Status |
|---|---|---|---|
| T05 BBMP Road | Must remain BID | BID | ✓ HELD |
| T06 NHAI Highway | Must remain NO_BID via threshold | NO_BID (turnover gap) | ✓ HELD |

## Remaining Open Failures

| Failure class | Count | Tenders | Status |
|---|---|---|---|
| PAT-001 false BIDs | 0 | — | Resolved by Epic 1 |
| PAT-003 still active | 1 | T10 (reasoning wrong) | Epic 2 not implemented |
| PAT-005 JV mandate | 1 | T10 (reasoning wrong) | Candidate, not promoted |
| Domain label error (wrong branch, correct FAIL) | 3 | T02, T03, T04 | v2 taxonomy improvement |

## Confidence Scores (Gate)

| Tender | Gate Decision | Confidence | is_clear |
|---|---|---|---|
| T01 | FAIL | 0.92 | True |
| T02 | FAIL | 0.92 | True |
| T03 | FAIL | 0.78 | False |
| T04 | FAIL | 0.92 | True |
| T05 | PASS | 0.90 | True |
| T06 | PASS | 0.90 | True |
| T07 | FAIL | 0.92 | True |
| T08 | FAIL | 0.92 | True |
| T09 | FAIL | 0.78 | False |
| T10 | PASS | 0.90 | True |

**Note on T03 and T09 (confidence 0.78 / is_clear=False):**
Both cases have a primary score < 2× secondary score. T03: building-construction 138 vs it-digitization 72 (1.9:1). T09: railway-metro 90 vs building-construction 48 (1.9:1). The decision is still correct but the extractor cannot assert single-branch dominance with high confidence.
