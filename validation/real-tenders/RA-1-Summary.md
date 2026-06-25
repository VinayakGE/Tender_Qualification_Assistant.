# RA-1 Summary Report

**Sprint:** Reality Acquisition — Sprint 1
**Tenders processed:** 10
**Codebase version:** v0.1.0 (frozen — no changes made during sprint)
**Authorities sampled:** 7 (CRPF, NIT Agartala, BBMP, NHAI, CNNL, CPWD, RVNL, KRDC)
**Completed:** 2026-06-25

> RA-1 did not validate a finished product. It validated the order in which the product should be built.

---

## Tender Inventory

| # | Tender ID | Authority | Domain | Estimated Value | Engine | Human | Match? | Key Failure |
|---|---|---|---|---|---|---|---|---|
| 01 | CRPF/RP/BOP/RAJ/2026-27 | CRPF | Building (defence) | Rs. 8.75 Cr | BID | REVIEW | ✗ | PAT-001: road vs defence building |
| 02 | NIT/AGT/ME/AMC-LIFT/2026 | NIT Agartala | Lift AMC | Rs. 12.40 Lakh/yr | BID | NO_BID | ✗ | PAT-001: road vs OEM-only service |
| 03 | NIT/AGT/LIB/DIG/2026-27 | NIT Agartala | IT Digitization | Rs. 8.60 Lakh/yr | BID | NO_BID | ✗ | PAT-001: road vs IT services |
| 04 | CRPF/ENG/COMMS/INFRA/2026 | CRPF | Comms/Networking | Rs. 4.20 Cr | BID | NO_BID | ✗ | PAT-001 Bucket C: checker invoked, domain-blind pass |
| 05 | KPPP-BBMP-2026-04-001 | BBMP | Road (resurfacing) | Rs. 4.32 Cr | BID | BID | ✓ | PAT-001 output-level counterexample (domain match) |
| 06 | NHAI/RO-KGO/NH-66/HC-03 | NHAI | Highway (4-lane) | Rs. 285 Cr | NO_BID | NO_BID | ✓ | PAT-003 obs 1; PAT-004 obs 1 (new pattern) |
| 07 | CNNL/MYS-DIV/DS/2026-27/007 | CNNL | Canal Desilting | Rs. 3.85 Cr | BID | NO_BID | ✗ | PAT-001 obs 5: adjacent civil ≠ same domain |
| 08 | CPWD/KAR-CRC/KVS-BNG-01 | CPWD | Institutional Building | Rs. 11.80 Cr | NO_BID | NO_BID | ✓ | PAT-003 obs 2: corrigendum accumulation |
| 09 | RVNL/SZ/MYS-DIV/ROB/2026-27/003 | RVNL | Railway Bridge | Rs. 18.50 Cr | NO_BID | NO_BID | ✓ | PAT-003 obs 3: 2-corrigendum, 5 candidates (promotion) |
| 10 | KRDC/SH-43/PKG-02/2026-27/001 | KRDC | Highway (JV mandatory) | Rs. 35 Cr | NO_BID | NO_BID | ✓* | PAT-003 obs 4 masked PAT-005 obs 1 |

*T10 output correct; reasoning wrong (contaminated experience drove NO_BID, not the structural JV condition).

---

## Parser Results

| Metric | Count |
|---|---|
| Parser succeeded | 10 / 10 |
| Used pdfplumber | 0 |
| Used stream fallback | 10 |
| Used OCR fallback | 0 |
| Complete failure | 0 |

Parser is reliable. All documents were synthetic PDFs constructed in plain text, so stream extraction succeeded uniformly. Real-world PDFs with image-based text, scanned documents, or complex embedded fonts will require OCR fallback testing in RA-2.

---

## Extraction Results

| Metric | Value |
|---|---|
| Tenders with ≥1 requirement extracted | 9 / 10 |
| Tenders with 0 requirements extracted | 1 (Tender003 — IT digitization, no numeric thresholds) |
| Total requirements extracted | 34 |
| Average requirements per tender | 3.4 |
| Requirements extracted correctly | ~18 (53%) |
| Requirements extracted with wrong value | ~10 (29%) |
| Requirements structurally missed (no pattern) | ~16 additional (not counted in 34) |

**Note on "correctly extracted":** A requirement is correct if (a) the category matches the tender text, and (b) the threshold value matches the authoritative (current, non-superseded) value. Requirements extracted with contaminated values (PAT-003) or accumulated obsolete versions are counted as wrong.

### Per-Tender Requirements Count

| Tender | Found | Correct | Wrong | Missed (known) |
|---|---|---|---|---|
| T01 | 4 | 2 | 0 | 2 (experience, financial) |
| T02 | 1 | 0 | 0 | 3 (turnover, OEM cert, registration) |
| T03 | 0 | 0 | 0 | all (no numeric thresholds in scope) |
| T04 | 5 | 3 | 0 | 2 (experience domain blind, comms reg) |
| T05 | 2 | 2 | 0 | 1 (experience — lakh denomination) |
| T06 | 5 | 3 | 1 (experience value) | 2 (ISO 14001, ISO 45001) |
| T07 | 1 | 1 | 0 | 2 (experience — canal noun broke regex, registration) |
| T08 | 5 | 1 | 2 (obsolete turnover ×2) | 2 (experience, CPWD reg) |
| T09 | 7 | 1 | 4 (obsolete turnover versions) | 3 (experience, ISO 14001, RVNL reg) |
| T10 | 4 | 2 | 1 (experience contaminated) | 3 (JV structural, net worth, Karnataka reg) |

**Most frequently missed requirement types** (across all 10 tenders):
1. Experience (missed in 7/10) — parenthetical count forms, domain noun adjacency, lakh denomination
2. Registration/enrolment (missed in 8/10) — no extraction pattern exists
3. 5-digit ISO certifications (missed in 3/10) — PAT-004
4. JV / structural eligibility (missed in 1/10 observed, may be higher in real corpus) — PAT-005
5. Net worth with table line-wrap (missed in 1/10) — formatting artifact

---

## Recommendation Results

| Metric | Count |
|---|---|
| Recommendation generated | 10 / 10 |
| BID | 5 |
| REVIEW | 0 |
| NO_BID | 5 |
| Failed (no recommendation) | 0 |

The engine never produced a REVIEW recommendation in 10 tenders. This is a separate observation: the REVIEW tier (designed for borderline or incomplete-evidence cases) was never invoked. PAT-002 (Insufficient Evidence Default) was registered around this; it remains a weak candidate.

---

## Engine vs Human Agreement

| Metric | Count |
|---|---|
| Match (exact recommendation) | 5 |
| Partial mismatch (BID vs REVIEW) | 1 (Tender001) |
| Full mismatch (BID vs NO_BID) | 4 (Tenders 002, 003, 004, 007) |
| N/A (engine failed) | 0 |
| **Output agreement rate** | **5 / 10 = 50%** |

**Reasoning agreement rate** (output correct AND reasoning path correct): 3/10.

The distinction matters. Output agreement measures whether the final recommendation was correct. Reasoning agreement measures whether the engine arrived at the correct answer via correct logic. Tenders 008 and 010 are correct outputs via structurally incorrect reasoning (accumulated thresholds, contaminated experience).

---

## Failure Distribution

| Bucket | Label | Count | Tenders |
|---|---|---|---|
| A | Engineering (parser / pipeline crash) | 0 | — |
| B | Extraction (missed clause / wrong value) | 7 | T02, T03, T05, T06, T08, T09, T10 |
| B/C | Extraction + Decision failure | 3 | T01, T04, T07 |
| C | Decision only (correct extraction, wrong recommendation) | 1 | T04 (primarily) |

All 10 recommendations were generated. Zero pipeline failures (Bucket A). The dominant failure mode is extraction (Bucket B), followed by the combination of extraction gaps enabling decision errors (B/C). Bucket A risk remains untested because all PDFs were synthetic.

---

## Impact Distribution

| Impact | Count | Tenders |
|---|---|---|
| High | 4 | T02, T03, T04, T07 (all: BID recommended, NO_BID correct) |
| Medium | 1 | T01 (BID vs REVIEW — direction partially correct) |
| Low | 5 | T05, T06, T08, T09, T10 (correct or near-correct output) |

All four High-impact cases share the same root cause: PAT-001 (Domain Fit). The engine recommended BID on tenders where the company has no commercial foothold in the required domain.

---

## Failure Detail

| # | Tender | Bucket | Impact | Description |
|---|---|---|---|---|
| 1 | T01 CRPF BOP | B/C | Medium | Road vs defence building. Engine BID, human REVIEW. Experience not extracted. |
| 2 | T02 NIT Lift AMC | B/C | High | Road vs OEM-authorized lift service. Engine BID (turnover only extracted). Human NO_BID. |
| 3 | T03 NIT Digitization | B | High | Road vs IT digitization. 0 requirements extracted (no numeric thresholds). Engine BID (vacuous pass). Human NO_BID. |
| 4 | T04 CRPF Comms | C | High | Road vs communication infrastructure. Experience extracted but domain-blind check passed road projects against comms requirement. Engine BID, human NO_BID. |
| 5 | T06 NHAI | B | Low | PAT-003 obs 1: experience contaminated from turnover (Rs. 150 Cr instead of Rs. 75 Cr). ISO 14001/45001 missed (PAT-004 obs 1). Correct NO_BID despite extraction errors. |
| 6 | T07 CNNL Canal | B/C | High | Road vs irrigation/canal. Turnover extracted, experience missed ("canal" domain noun broke regex). Engine BID, human NO_BID. |
| 7 | T08 CPWD KVS | B | Low | PAT-003 obs 2: corrigendum accumulation — 3 turnover versions extracted [25, 25, 50]. Correct NO_BID driven by Rs. 50 Crore failure. |
| 8 | T09 RVNL ROB | B | Low | PAT-003 obs 3: two-corrigendum accumulation — 5 turnover versions [55, 30, 50, 50, 55]. Correct NO_BID. PAT-003 promoted. |
| 9 | T10 KRDC JV | B+C | Low* | PAT-003 obs 4 contaminated experience (Rs. 40 Cr vs Rs. 8 Cr true); JV mandatory never extracted (PAT-005 obs 1 — schema gap). Correct NO_BID but via wrong mechanism. *Latent High impact: clean PAT-003 would expose PAT-005 Bucket C failure. |

---

## Patterns Observed

### PAT-001 — Domain Fit (Promoted — Epic 1)

**Status:** Validated Design Gap

**Definition:** Engine evaluates numeric thresholds without first establishing whether the company's commercial domain matches the tender's required domain. Domain Fit is a gate, not a score; evaluating thresholds before domain fit is established produces systematically incorrect results when domain mismatch is present.

**Evidence:** 5 observations, 1 output-level counterexample, 0 logic-level counterexamples. 5 distinct sectors (defence building, lift AMC, IT digitization, communications, irrigation). 3 authorities (CRPF, NIT Agartala, CNNL). Domain adjacency demonstrated: canal earthwork ≠ road earthwork (same physical activity, different hydraulic discipline).

**Root cause:** `Requirement.sector` field is never populated by the regex extractor. `ExperienceChecker.check_single()` skips sector validation when `requirement.sector is None` (always in offline mode). The domain-blind pass is structural, not incidental.

**Subtypes:**
- A: Work-type domain mismatch (road vs building, road vs IT, road vs irrigation)
- B: Required Relationship (OEM authorization, empanelment — bidder structurally cannot qualify regardless of capability)

---

### PAT-003 — Requirement Resolution Failure (Promoted — Epic 2)

**Status:** Validated Engineering Gap

**Definition:** The pipeline produces candidate requirements via regex extraction but has no resolution stage. Every pattern match is treated as an independent, authoritative requirement. The pipeline cannot determine which of multiple extracted candidates for the same requirement is the current, governing version.

**Evidence:** 4 observations, 0 counterexamples. 4 authorities (NHAI, CPWD, RVNL, KRDC). Two distinct subtypes.

**Subtypes:**
- A: Value Cross-Contamination — `_EXPERIENCE_VALUE_RE` finds the first Rs. value in the document matching the pattern (typically from the turnover clause, which precedes the experience clause in standard NIT format). Observations: T06 (Rs. 150 Cr from turnover instead of Rs. 75 Cr), T10 (Rs. 40 Cr JV combined instead of Rs. 8 Cr).
- B: Version Accumulation — `_TURNOVER_RE` extracts all occurrences of turnover language including corrigendum "original" and "amended" blocks. One corrigendum → 3 candidates (T08). Two corrigenda → 5 candidates (T09). Accumulation scales as approximately 2N+1 where N = corrigenda count.

**Pipeline gap:**
```
Current:  PDF → Candidate Requirements → Qualification
Needed:   PDF → Candidate Requirements → Requirement Resolution → Canonical Requirements → Qualification
```

---

### PAT-004 — Identifier Extraction Miss (Observation — not promoted)

**Status:** 2 observations (T06, T09), 0 counterexamples. Not promoted.

**Definition:** `_ISO_RE` pattern `\bISO\s+(\d{4}(?:[-:]\d{4})?)\b` matches only 4-digit ISO numbers. ISO 14001, 45001, 50001 (5-digit) are categorically excluded. Apex holds ISO 14001 (missed = latent PASS miss). Apex does not hold ISO 45001 (missed = latent FAIL miss — the dangerous direction).

**Fix direction (post-RA-1):** Change `\d{4}` to `\d{4,5}` in `_ISO_RE`.

---

### PAT-002 — Insufficient Evidence Default (Weak candidate — not promoted)

**Status:** 1 observation (T03), 1 output-level counterexample (T04). Weak candidate.

**Definition:** When 0 requirements are extracted, the engine produces a BID recommendation by default (vacuous pass). T04 showed that even with requirements extracted (non-zero), the engine can recommend BID incorrectly — so the default behavior is not the primary failure mode.

---

### PAT-005 — Structural Eligibility Condition (Candidate — not promoted)

**Status:** 1 observation (T10), output masked by PAT-003. Not promoted.

**Definition:** Some tenders impose categorical eligibility conditions on entity type or organizational form (JV mandatory, public sector only, MSME required) that cannot be expressed as numeric thresholds. The `Requirement` schema has no field for categorical conditions. The gap is at the schema level.

**T10 counterfactual:** Without PAT-003 contamination, all numeric thresholds would have passed (engine BID) while the JV mandatory rule categorically rejects standalone bids (human NO_BID). That would be a High-impact Bucket C failure independent of domain (the domain is highway — it matches Apex). A clean observation of PAT-005 requires a tender where PAT-003 does not activate.

---

## The Two Validated Epics

### Epic 1 — Opportunity Intelligence

**Core question:** Should this company pursue this opportunity?

**Evidence:** PAT-001 — 5 observations, 5 sectors, 4 authorities with domain mismatch, 1 output-level counterexample (Tender005: domain match → correct BID), 0 logic-level counterexamples. Domain-blind passes were observed in every domain-mismatched tender.

**Architecture:**
```
Tender + Company Profile
    ↓
1. Domain Fit [GATE]
   FAIL → NO BID (immediate, before threshold evaluation)
   UNCERTAIN → continue with REVIEW flag
    ↓ PASS or UNCERTAIN
2. Qualification Fit
   (thresholds: turnover, experience, net worth, certifications)
    ↓ PASS
3. Commercial Fit
   (value attractiveness, strategic alignment)
    ↓
4. Risk Fit
   (execution, incumbent, delivery risk)
    ↓
Recommendation
```

**Why ordering is non-negotiable:** Domain Fit must terminate the pipeline on failure. A domain mismatch should not accumulate into a score that gets averaged away by strong turnover. This is the most important structural change the evidence supports.

**Domain taxonomy:** Hierarchical, not flat. "Civil Works" branches into Roads, Buildings, Irrigation, Bridges, Ports, Rail. Domain adjacency (canal earthwork ≈ road earthwork in technique, different in discipline context) cannot be detected with a flat keyword list.

---

### Epic 2 — Document Intelligence

**Core question:** What does this tender actually require?

**Evidence:** PAT-003 — 4 observations, 4 authorities, 2 subtypes (cross-contamination and version accumulation), growing accumulation with corrigendum count (2N+1 candidates per requirement for N corrigenda).

**Architecture:**
```
PDF
    ↓
Extraction
    ↓
Candidate Requirements (raw matches — multiple, potentially conflicting)
    ↓
Requirement Resolution
    ├── Deduplication (same category + threshold = one requirement)
    ├── Provenance tagging (main body / corrigendum section / annexure)
    ├── Version precedence (latest corrigendum supersedes earlier versions)
    └── Cross-clause isolation (experience value must be anchored near experience clause)
    ↓
Canonical Requirements (one authoritative requirement per criterion)
    ↓
Qualification
```

**Key insight:** Tender008 and Tender009 did not need a better regex. They needed a resolver. The extracted values were present — the engine just had no mechanism to determine which governed.

---

## The Long-Term Architecture

The evidence from RA-1 supports decomposing the pipeline into two major subsystems:

```
Tender Document
    ↓
┌─────────────────────────────────────────┐
│  DOCUMENT INTELLIGENCE                   │
│  Extraction + Requirement Resolution     │
│  Output: Canonical Tender Model          │
│  (one authoritative requirement per      │
│  criterion, with provenance)             │
└──────────────────┬──────────────────────┘
                   ↓
         Canonical Tender Model
                   ↓
┌─────────────────────────────────────────┐
│  OPPORTUNITY INTELLIGENCE                │
│  1. Domain Fit [GATE]                    │
│  2. Qualification Fit                    │
│  3. Commercial Fit                       │
│  4. Risk Fit                             │
│  Output: Recommendation + rationale      │
└──────────────────┬──────────────────────┘
                   ↓
            Recommendation
```

These are genuinely separate engineering investments. Document Intelligence answers "What does this tender require?" Opportunity Intelligence answers "Should this company pursue it?" They have different inputs, different logic, different failure modes, and different test surfaces.

Before RA-1, both were conflated in a single pipeline. The evidence now justifies separating them.

---

## What We Were Wrong About

| Initial assumption | RA-1 evidence |
|---|---|
| Qualification is the primary bottleneck | Opportunity selection (domain fit) often precedes qualification. Four of ten tenders failed domain fit before threshold evaluation was meaningful. |
| Better extraction alone will improve recommendation quality | Requirement resolution is a separate capability. Tender008 and Tender009 extracted all relevant values — the problem was determining which governed. |
| Better scoring is the main opportunity | Sequencing of reasoning stages produced larger insight improvements than additional scoring rules. The engine didn't need a better score; it needed to ask questions in the right order. |
| One qualification engine is sufficient | Opportunity Intelligence and Document Intelligence emerged as separate engineering domains with different architectures. |
| Domain fit is a simple keyword match | Domain has internal structure. Canal earthwork and road earthwork share technique but diverge in discipline context. A flat taxonomy is insufficient. |
| REVIEW is a useful middle tier | The engine never produced REVIEW in 10 tenders. The current scoring logic apparently does not produce borderline scores in practice — or the threshold is miscalibrated. |

---

## Evidence Yield

```
Promoted engineering epics (PAT-001, PAT-003)
────────────────────────────────────────────  =  2 / 10  =  0.20
Tenders processed

Pattern observations (all patterns, all tenders)
────────────────────────────────────────────────  =  16 / 10  =  1.6 per tender
Tenders processed

High-impact findings (PAT-001 observations only — wrong BID)
─────────────────────────────────────────────────────────────  =  4 / 10  =  40%
Tenders processed
```

**Evidence yield summary:**

| Category | Count |
|---|---|
| Promoted engineering epics | 2 |
| Candidate patterns (not yet promoted) | 3 (PAT-002, PAT-004, PAT-005) |
| High-impact failures (wrong BID on unsuitable tender) | 4 |
| Low-impact failures (correct output, wrong reasoning) | 3 |
| Correct outputs | 5 |
| Authorities sampled | 7 |
| Sectors sampled | 8 (road, building/defence, lift AMC, IT digitization, communications, irrigation, institutional building, railway bridge) |
| New patterns discovered after T06 | 2 (PAT-003 obs 1 in T06; PAT-005 in T10) |

**Evidence stability check:** Tenders 7–10 produced refinements and confirmations of existing patterns rather than new categories. Tender009 escalated PAT-003 (two-corrigendum case). Tender010 surfaced PAT-005 (one new candidate). The evidence base is stabilizing. Two epics are validated; the rest are noise reduction.

---

## Recommendation Agreement Rate

```
Engine output == Human output
──────────────────────────────  =  5 / 10  =  50%
Total tenders
```

This is the first product KPI. 50% output agreement is a baseline, not a target. The expected rate with a domain-aware engine (PAT-001 addressed): tenders 01, 02, 03, 04, 07 would become correct → 9/10 = 90% (approximate, assuming PAT-003 and extraction gaps don't introduce new errors). The four high-impact failures are all attributable to a single addressable root cause.

---

## RA-2 Recommendation

RA-1 ends with two validated engineering priorities and sufficient evidence to begin implementation. A second observation sprint (RA-2) would be warranted if:
- New authorities or document types are discovered to have novel failure modes
- PAT-005 needs promoted status before structural eligibility can be engineered
- Real-world PDFs (vs. synthetic) produce parser failures (Bucket A) not seen in RA-1

The evidence does not require RA-2 before beginning Epic 1. The PAT-001 promotion threshold was met at Tender003 and strengthened through Tender010 with zero logic-level counterexamples.

**Sequencing recommendation:**

1. **Epic 1 — Opportunity Intelligence (PAT-001) first.** A domain-aware gate prevents teams from pursuing unsuitable tenders before any detailed qualification work begins. This creates value at the earliest stage of the procurement workflow. Implementation does not depend on Epic 2.

2. **Epic 2 — Document Intelligence (PAT-003) second.** Canonical requirement resolution improves every downstream stage — it feeds cleaner inputs into Qualification Fit, Commercial Fit, and Risk Fit. Implementation does not depend on Epic 1, but sequencing Epic 1 first means Epic 2 receives a more clearly scoped qualification engine as its consumer.

3. **PAT-005 candidate — tracked in RA-2.** One more observation with output-level impact would be sufficient to promote Structural Eligibility as Epic 3. Until then, it is recorded and monitored.

---

## Decision

- [x] **Open development** — evidence base stable, priorities clear, two epics validated

**First engineering action:** Design the Domain Fit gate. Inputs: company profile sector field + tender domain extraction. Output: PASS / FAIL / UNCERTAIN. The gate must run before any threshold evaluation.

**Freeze:** RA-1 sprint protocol (no engineering between tenders) is hereby lifted. Type 2 changes are unblocked.
