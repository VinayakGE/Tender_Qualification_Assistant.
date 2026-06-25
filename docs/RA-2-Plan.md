# RA-2 Plan — Domain Fit Gate

**Sprint:** Reality Acquisition — Sprint 2
**Scope:** One epic. One measurable improvement.
**Status:** Open — implementation begins after this plan is reviewed

---

## Goal

> Reduce false-positive BID recommendations by implementing a Domain Fit gate.

The RA-1 baseline shows 4 high-impact false BIDs in 10 tenders, all attributable to the same root cause: the engine evaluated thresholds on domain-mismatched tenders without first checking whether the company's commercial domain matches the tender's required domain.

RA-2 answers a single question:

> Does implementing the Domain Fit gate reduce false BIDs, and at what cost to false NO_BIDs?

---

## What We Are Building

**Epic 1 — Domain Fit Gate (PAT-001 engineering response)**

A gate that runs before any threshold evaluation. It takes two inputs:
1. Company profile: declared sector, completed project sectors
2. Tender: extracted domain keywords, required work type

And produces one output: PASS / FAIL / UNCERTAIN.

- **FAIL** → pipeline terminates → NO_BID (with rationale: domain mismatch)
- **UNCERTAIN** → pipeline continues with REVIEW flag (domain could not be determined)
- **PASS** → pipeline continues as before

The gate must be the first check. A domain-mismatch FAIL does not produce a qualification score. It produces a domain-fit reason and immediate NO_BID.

### Minimum Viable Domain Fit Gate

The gate does not require a perfect domain taxonomy on day one. The minimum viable implementation:

1. **Tender domain extraction:** detect the primary work type from tender text (keyword-based initially). Candidate signals: "road / highway", "building / construction", "lift / elevator", "canal / irrigation", "communication / networking", "digitization / scanning", "bridge / ROB".

2. **Company domain:** read from `company_profile.sector` field. Currently always "road-construction" for Apex. This field must be populated and maintained.

3. **Match logic (v1):** simple keyword set intersection. If tender domain and company domain share no keywords from the same domain branch → FAIL. If uncertain (keywords absent or ambiguous) → UNCERTAIN.

4. **Taxonomy (v1):** two-level flat hierarchy is acceptable for the first version. Full hierarchical taxonomy (see `docs/OFE-candidate.md`) is a v2 target.

### What We Are Not Building in RA-2

- Epic 2 (Requirement Resolution / PAT-003): deferred until RA-2 benchmark results are published
- PAT-005 (Structural Eligibility): tracked, not implemented
- Scoring changes: the qualification score, commercial score, and risk score are not modified
- New extraction patterns: PAT-004 fix (`\d{4}` → `\d{4,5}`) is low-risk but deferred to keep attribution clean

---

## Success Criteria

The Domain Fit gate is successful if, when the same 10 RA-1 tenders are re-run:

| Criterion | Target |
|---|---|
| False BIDs (engine BID, human NO_BID) | Reduced from 4 to ≤1 |
| Recommendation Agreement Rate | Increased from 50% to ≥80% |
| New false NO_BIDs introduced | 0 (domain gate must not misfire on T05, T06, T08, T09) |
| T05 (BBMP road — domain match) | Still BID |
| UNCERTAIN flag on ambiguous cases | Present where domain cannot be determined |

### Failure definition

The gate fails if:
- It misfires on a domain-matched tender (T05, T06, T08, T09, T10) → false NO_BID
- It passes a clearly domain-mismatched tender (T01–T04, T07) → false BID unchanged
- It produces UNCERTAIN on a clearly domain-matched tender

---

## Benchmark Protocol

After Epic 1 implementation:

1. Re-run all 10 RA-1 tenders unchanged (same PDFs, same company profile)
2. Record engine recommendation, domain-fit gate output, and qualification score
3. Compare against RA-1 baseline
4. Publish RA-2-Delta-Report.md with the metrics below

**The benchmark is the same 10 tenders. No new tenders in RA-2.** Adding new tenders would confound the measurement — any change in agreement rate could be due to new tender characteristics, not to the Epic 1 implementation.

---

## RA-2 Delta Report Template

To be filled after Epic 1 is implemented and the 10 tenders are re-run.

### Recommendation Agreement

| Metric | RA-1 Baseline | RA-2 Result | Delta |
|---|---|---|---|
| Output agreement rate | 50% (5/10) | — | — |
| False BIDs (BID / NO_BID mismatch) | 4 (T02, T03, T04, T07) | — | — |
| False NO_BIDs (NO_BID / BID mismatch) | 0 | — | — |
| Reasoning agreement rate | 30% (3/10) | — | — |

### Domain Fit Gate Performance

| Tender | Domain Required | Gate Output (RA-2) | Correct? |
|---|---|---|---|
| T01 CRPF BOP | Defence building | — | Expected: FAIL |
| T02 NIT Lift | Lift AMC | — | Expected: FAIL |
| T03 NIT Digitization | IT digitization | — | Expected: FAIL |
| T04 CRPF Comms | Communications | — | Expected: FAIL |
| T05 BBMP Road | Highway / road | — | Expected: PASS |
| T06 NHAI Highway | Highway / road | — | Expected: PASS |
| T07 CNNL Canal | Irrigation / canal | — | Expected: FAIL |
| T08 CPWD KVS | Institutional building | — | Expected: FAIL |
| T09 RVNL ROB | Railway / bridge | — | Expected: FAIL |
| T10 KRDC Highway | Highway / road | — | Expected: PASS |

**Gate precision:** Correct FAILs / Total FAILs issued
**Gate recall:** Correct FAILs / Total mismatched tenders

### New Failure Classes

| Category | Count in RA-2 | Notes |
|---|---|---|
| Domain gate misfire (false NO_BID) | — | Must be 0 |
| UNCERTAIN on domain-matched tender | — | Must be 0 |
| New extraction failures surfaced | — | Document any |
| PAT-003 still present (accumulation) | Expected: yes | Epic 2 not yet implemented |

### KPI Dashboard

| KPI | RA-1 | RA-2 | Direction |
|---|---|---|---|
| Recommendation Agreement Rate | 50% | — | ↑ target ≥80% |
| Domain Fit Detection Rate (FAIL on mismatch) | 0% | — | ↑ target ≥85% |
| False BID Rate | 40% (4/10) | — | ↓ target ≤10% |
| Canonical Requirement Accuracy | ~53% | — | → unchanged (Epic 2 not implemented) |

---

## Sequencing Rationale

Epic 1 before Epic 2 for two reasons, both from evidence:

**1. Attribution clarity.** If both epics are implemented together, improvement in the agreement rate cannot be attributed to either one alone. RA-2 measures Epic 1 in isolation. RA-3 (if warranted) measures Epic 2 against the RA-2 baseline.

**2. Value priority.** Domain Fit is a gate that creates value before any document analysis begins. A bid team that receives an immediate "domain mismatch — do not evaluate" signal saves more time than a bid team that receives a more accurate set of extracted requirements. Epic 1 reaches the customer sooner.

---

## What Remains Frozen Until RA-2 Benchmark Is Published

- Epic 2 (PAT-003 Requirement Resolution): implementation blocked
- Any scoring model changes
- Changes to the qualification threshold logic
- PAT-005 structural eligibility implementation

The freeze is narrow — only Epic 1 is unblocked. This keeps the causal chain clean: RA-2 agreement rate improvement = Epic 1 contribution, not a mixed signal from multiple changes.
