# Evidence Index

**Purpose:** One-page record of what has been demonstrated versus what remains a hypothesis. No narrative. Append only — prior rows are never edited.

Last updated: 2026-06-26 (market validation restructured into three stages: Decision Validation → Workflow Validation → Commercial Validation)

---

## Epic Evidence

| Epic | Engineering Change | Supporting Patterns | Observations | Benchmark Evidence | Current Status |
|---|---|---|---|---|---|
| Opportunity Intelligence — Domain Fit | Domain Fit Gate (`src/domain/`) | PAT-001 (5 obs, 1 output-level CX, 0 logic-level CX) | T01, T02, T03, T04, T07 | RA-1 (false BID exposed), RA-2 (false BID eliminated, 50%→100% agreement) | **Implemented — RA-2** |
| Document Intelligence — Requirement Resolution | Resolver pipeline stage (not yet built) | PAT-003 (4 obs, 4 authorities: NIT, CPWD, RVNL, KRDC) | T06, T08, T09, T10 | RA-1 (contamination and accumulation documented) | **Planned — Epic 2, blocked on RA-2.5** |
| Structural Eligibility | Entity condition checker (not yet built) | PAT-005 (1 obs, output masked by PAT-003) | T10 | RA-1 (schema gap confirmed) | **Candidate — not promoted** |
| Identifier Extraction Fix | `\d{4}` → `\d{4,5}` regex change | PAT-004 (2 obs, no authority replication) | T06, T09 | RA-1 (missed 5-digit ISO standards) | **Candidate — not promoted** |

---

## Pattern Evidence

| Pattern | Definition | Observation Count | Authorities | Output-Level Impact | Bucket | Status |
|---|---|---|---|---|---|---|
| PAT-001 Domain Fit | Pipeline evaluates thresholds without checking domain compatibility | 5 | CRPF, NIT, CNNL (×2), RVNL | 4 false BIDs in RA-1; eliminated in RA-2 | C (Decision) | Promoted → Implemented |
| PAT-003 Requirement Resolution | Candidate requirements not resolved to canonical set: Subtype A (cross-contamination), Subtype B (version accumulation) | 4 | NIT, CPWD, RVNL, KRDC | T06 experience contaminated; T08/T09 turnover accumulated; T10 experience contaminated | B (Extraction) | Promoted → Epic 2 planned |
| PAT-004 Identifier Extraction | `_ISO_RE` uses `\d{4}`, misses 5-digit standards (14001, 45001, 50001) | 2 | NHAI, RVNL | ISO 14001 / 45001 missed in T06, T09 | B (Extraction) | Candidate — not promoted |
| PAT-005 Structural Eligibility | No schema field for categorical eligibility conditions (JV mandatory, public-sector-only, MSME) | 1 | KRDC | T10 output correct but masked by PAT-003 | C (Decision) | Candidate — not promoted |

---

## Benchmark Evidence

| Suite | Tenders | Profiles | Completed | Key Finding |
|---|---|---|---|---|
| suite-RA1 | 10 | 1 (Apex, road) | RA-1 (2026-06-25), RA-2 (2026-06-26) | Domain Fit Gate eliminated 4 false BIDs; 50%→100% output agreement |
| suite-RA25 | 24 | 3–5 (multi-sector) | Planned — RA-2.5 | Generalization test for Domain Fit; authority-conflation hypothesis |

---

## Architecture Evidence

| Claim | Evidence Source | Status |
|---|---|---|
| Domain Fit must precede Qualification | PAT-001 (5 obs), RA-2 benchmark (100% agreement after gate implemented) | Validated |
| Requirement Resolution is a separate pipeline stage | PAT-003 (4 obs, 2 subtypes, 4 authorities) | Validated — not yet implemented |
| Flat domain taxonomy is insufficient | T07 (canal ≠ road despite both being civil earthwork), T09 (ROB is railway not road) | Validated |
| Structural eligibility requires schema extension | T10 (JV mandate cannot be expressed as numeric threshold) | Validated at schema level — 1 observation |
| REVIEW tier is not useful in current form | 0 REVIEW outputs in 10 RA-1 tenders; all decisions binary BID/NO_BID | Observed — not yet addressed |

---

## What Has NOT Been Demonstrated

Explicit record of what remains hypothesis.

| Claim | Current State | Evidence Required to Promote |
|---|---|---|
| Domain Fit Gate generalizes beyond RA-1 benchmark | Unvalidated — 10 tenders, 1 profile only | RA-2.5: ≥85% agreement on 24 unseen tenders across 3–5 profiles |
| Requirement Resolution will raise agreement further | Hypothesis — PAT-003 is active but Epic 2 not implemented | RA-3: RA-3 agreement > RA-2.5 agreement on same suite |
| PAT-004 fix improves decision quality | Candidate — 2 observations, no confirmed output-level impact | 1 more observation with output-level impact; or RA-2.5 surfaces ISO miss causing false BID |
| PAT-005 fix is warranted | Candidate — 1 observation, output masked | 1 more observation with confirmed output-level impact (engine BID / human NO_BID on structurally ineligible tender) |
| Domain taxonomy is sufficient for commercial use | Unknown — only 8 branches, 1 company sector tested | RA-2.5 multi-profile run; authority-conflation hypothesis verdict |
| **Stage A — Decision Validation (DV-1)** | | |
| Engine reasoning sequence matches experienced decision owner reasoning | Unvalidated — no live Go/No-Go decisions observed | Observe 10 real Go/No-Go decisions across ≥3 Decision Laboratories (EPC contractors, tender consultants, proposal managers); compare reasoning sequence step-by-step, not just final output; record divergences without explaining them. Unit of evidence: the decision, not the organization. |
| Engine surfaces information the evaluator had not already considered | Unvalidated | Record per-decision: did engine output add any signal the human did not have? Was that signal used, ignored, or disputed? |
| **Stage B — Workflow Validation** | | |
| Engine fits into how teams actually make the Go/No-Go decision | Unvalidated — Stage A must complete first | Measure: time saved, steps removed, information available earlier in the process, whether evaluators return to the engine without prompting |
| Reasoning Divergence Rate is low enough to build trust | Unvalidated | After ≥10 live observations: classify each decision as same reasoning / different reasoning same conclusion / different reasoning different conclusion. Target: <20% different-reasoning-different-conclusion |
| **Stage C — Commercial Validation** | | |
| Value is large enough that organizations adopt and pay | Unvalidated — Stage B must complete first | Repeat usage without prompting; budget owner engagement; procurement process initiated |
| Development methodology generalizes to a second decision owner's context | Unvalidated — RA cycle built against one company's tenders and verdicts | Run one full RA cycle using a second organization's actual tenders and their own human verdicts; partial evidence from RA-2.5 multi-profile run |
