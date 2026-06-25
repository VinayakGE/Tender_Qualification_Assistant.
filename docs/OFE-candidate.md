# Opportunity Fit Engine — Candidate Architecture

**Status: Strengthened candidate — do not implement**
**Origin: RA-1 Reality Acquisition sprint, derived from Tender001–004 evidence**
**Evidence Gate: RA-1-Summary.md must be complete before this document advances to engineering**

---

## What RA-1 Is Revealing

The current MVP pipeline assumes that if a company clears numeric thresholds (turnover, experience value, count), they are qualified. Four tenders have tested this assumption. All four produced a wrong recommendation. The failure is not in the threshold math — it is in the question the pipeline never asks:

> What business is this company actually in?

That question precedes every threshold. It cannot be answered by comparing numbers.

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

**Evidence from RA-1:**
- Tender001: road contractor vs defence building → FAIL should have been immediate
- Tender002: road contractor vs Otis lift AMC (OEM cert required) → FAIL; this is Subtype B (Required Relationship), a structural incompatibility not just a capability gap
- Tender003: road contractor vs IT digitization → FAIL; experience metric is pages scanned, not rupee value

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
