# Opportunity Fit Engine — Candidate Architecture

**Status: Validated candidate — do not implement**
**Origin: RA-1 Reality Acquisition sprint, derived from Tender001–006 evidence**
**Evidence Gate: RA-1-Summary.md must be complete before this document advances to engineering**

---

## What RA-1 Is Revealing

Six tenders have been processed. The evidence now supports a three-layer model of what the pipeline actually does (and what it fails to do):

**Layer 1 — Domain Fit** (PAT-001, validated)
The pipeline has no mechanism to ask: "Is this opportunity in the company's commercial domain?" It evaluates thresholds without establishing domain compatibility first. Four of six tenders exposed this gap. Tender006 defined its boundary: when domain matches, the qualification logic works correctly.

**Layer 2 — Threshold Qualification** (validated by Tender006)
When domain is established and thresholds clearly fail, the engine correctly produces NO_BID. Turnover comparison, mandatory failure detection, and recommendation propagation all function correctly. This layer is not fundamentally broken.

**Layer 3 — Extraction Quality** (candidates PAT-003, PAT-004)
The regex extractor has structural coverage gaps: experience values are contaminated by turnover clauses (PAT-003), and 5-digit ISO standard numbers are categorically excluded from extraction (PAT-004). These are Bucket B issues — they affect the inputs to Layer 2 without breaking Layer 2's logic.

The three-layer framing is not a design proposal — it is a description of what the evidence reveals. The OFE candidate architecture below reflects this structure.

**The core MVP assumption that is false:** Domain fit is assumed before the pipeline runs. In practice, the pipeline is asked to evaluate domain-mismatched tenders with no mechanism to detect the mismatch. Tender001–004 all demonstrated this. Tender006 confirmed that removing the domain mismatch (by using a domain-matched tender) does not expose a broken qualification engine — it exposes a working one.

---

## Current Pipeline (MVP)

```
PDF
  │
  ▼
Extract Requirements
  │  [turnover, experience value, certifications]
  ▼
Check Thresholds
  │  [company value ≥ requirement threshold?]
  ▼
Score
  │  [qualification, competitiveness, risk]
  ▼
Recommend
  │  [BID / REVIEW / NO BID]
  ▼
Output
```

**Implicit assumption:** domain fit is already established before the pipeline runs. This assumption is false in practice — the pipeline is asked to evaluate a road contractor against a lift maintenance contract and it has no mechanism to detect the mismatch.

---

## Candidate: Opportunity Fit Engine

The ordering is not an implementation detail — it is the core claim. Domain Fit must run before Qualification Fit. You should never evaluate thresholds before establishing that the company's work domain matches the tender's work domain. Tender004 made this concrete: the experience threshold was extracted and evaluated correctly, but the evaluation was meaningless because the experience domain was never checked.

```
PDF + Company Profile
  │
  ▼
┌─────────────────────────────────┐
│  1. Domain Fit  [GATE]           │
│  Does the company's commercial   │
│  domain match the tender's       │
│  required domain?                │
│  → PASS / FAIL / UNCERTAIN       │
│                                  │
│  FAIL → pipeline terminates      │
│         → NO BID                 │
│  UNCERTAIN → pipeline continues  │
│              with REVIEW flag    │
└──────────────┬──────────────────┘
               │ PASS or UNCERTAIN
               ▼
┌─────────────────────────────────┐
│  2. Qualification Fit            │
│  Do the company's numeric        │
│  credentials meet the tender's   │
│  extracted thresholds?           │
│  Includes: value, count,         │
│  AND experience domain           │
│  → PASS / FAIL                   │
└──────────────┬──────────────────┘
               │ PASS only
               ▼
┌─────────────────────────────────┐
│  3. Commercial Fit               │
│  Is the tender commercially      │
│  attractive? Value, margin,      │
│  pipeline fit?                   │
│  → Score 0–100                   │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│  4. Risk Fit                     │
│  Execution, incumbent, and       │
│  delivery risk assessment.       │
│  → Score 0–100                   │
└──────────────┬──────────────────┘
               ▼
Recommend
  [BID / REVIEW / NO BID + rationale]
```

**Why ordering is non-negotiable:** Domain Fit is a gate, not a score. A domain mismatch terminates the pipeline early — it must not accumulate into a score that gets averaged away by strong turnover numbers. The current pipeline has no gate; it scores everything and recommends BID on a perfect score derived from a vacuous or domain-blind pass.

---

## Four Modules

### 1. Domain Fit (gate)

**What it checks:** Is the company's primary operating domain compatible with what this tender requires?

**Inputs:**
- Company profile: declared sector, completed projects (type, not just value)
- Tender: extracted work type, required domain keywords, authorization relationships

**Output:** PASS / FAIL / UNCERTAIN
- PASS: domain match detected
- FAIL: domain mismatch detected → pipeline terminates → NO BID
- UNCERTAIN: domain cannot be determined from available signals → pipeline continues with REVIEW flag

**Domain taxonomy: hierarchical, not flat.**
Tender007 showed that "civil works" is not one domain — it has internal structure. Road construction and canal desilting are both civil earthwork, but they are distinct domains (highway engineering vs hydraulic engineering). A flat taxonomy (Road / Building / IT / Electrical / Healthcare) is insufficient. The design requires at minimum a two-level hierarchy:

```
Civil Works
├── Roads & Highways
├── Buildings & Structures
├── Irrigation & Canals
├── Bridges
├── Ports & Marine
└── Rail & Metro

Mechanical / Electromechanical
├── Lifts & Escalators (Subtype B: OEM required)
├── HVAC / MEP
└── Power & Transmission

IT & Digital
├── Software / Systems
├── Digitization & Scanning
├── Communication & Networking
└── SCADA & Instrumentation
```

The implication for implementation: domain matching cannot use a simple keyword list. It requires understanding that "canal earthwork" and "road earthwork" are in different subtrees, even though the physical activity is similar.

**Evidence from RA-1:**
- Tender001: road contractor vs defence building → FAIL should have been immediate
- Tender002: road contractor vs Otis lift AMC (OEM cert required) → FAIL; this is Subtype B (Required Relationship), a structural incompatibility not just a capability gap
- Tender003: road contractor vs IT digitization → FAIL; experience metric is pages scanned, not rupee value
- Tender007: road contractor vs canal desilting → FAIL; same civil earthwork, different domain branch (highway vs hydraulic)

### 2. Qualification Fit (current pipeline, refined)

**What it checks:** Do numeric credentials meet extracted thresholds?
**Status:** Largely implemented. Key gap: domain-specific experience thresholds (sector type, page counts, unit-based requirements) are not currently extractable by regex.

### 3. Commercial Fit (current scoring, refined)

**What it checks:** Value attractiveness, strategic fit, win probability given competitive landscape.
**Status:** Partially implemented (value_score, competitiveness_score). Needs domain-aware calibration.

### 4. Risk Fit (current scoring, refined)

**What it checks:** Execution risk, incumbent risk, delivery timeline risk.
**Status:** Partially implemented (execution_risk, incumbent_risk). Generally domain-agnostic.

---

## Why This Matters for the Product

The current MVP is described as "Procurement Decision Intelligence." The evidence from RA-1 suggests the more precise framing is:

**Current:** Threshold checker with a scoring layer
**Candidate:** Opportunity Fit Engine — a structured filter that asks questions in the right order

The order matters. Domain Fit asks: "Should we evaluate this at all?" Qualification Fit asks: "Do we meet the bar?" Commercial Fit asks: "Do we want this?" Risk Fit asks: "Can we execute?"

Asking these out of order produces systematically wrong answers when domain mismatch is present.

---

## Evidence Required to Advance

This document is a candidate, not a plan. It advances when:

1. RA-1-Summary.md is complete
2. PAT-001 (Domain Fit) maintains zero counterexamples through RA-1
3. At least one additional failure class beyond PAT-001 and PAT-002 is observed (or absence of such is noted)
4. A domain taxonomy for Indian government procurement is drafted and reviewed

**Do not implement any component of this architecture until these gates are cleared.**
