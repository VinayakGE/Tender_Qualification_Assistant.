# Tender 10

## Source

| Field | Value |
|---|---|
| Portal | Synthetic — KRDC e-Procurement format |
| Tender ID / Reference | KRDC/SH-43/PKG-02/2026-27/001 |
| Issuing Authority | Karnataka Road Development Corporation Ltd (KRDC), Bengaluru |
| Work Description | 4-laning of State Highway-43 (Kalaburagi to Bidar), Package 02, Ch. 48+200 to Ch. 82+800 (34.6 km). Pavement widening, structures (3 bridges, 12 culverts), road furniture. KSHIP Phase III funded. |
| Estimated Value | Rs. 35,00,00,000/- (Rs. 35 Crore); EMD: Rs. 70,00,000/- |
| Download URL | Synthetic — KRDC format |
| Downloaded On | 2026-06-25 |
| Note | Final RA-1 tender. Designed to search for a third engineering epic. Deliberate design: JV mandatory (standalone bids explicitly rejected), domain matches Apex (highway), all numeric thresholds individually below Apex's profile. Intended outcome: PAT-005 candidate (Structural Eligibility Condition), clean Bucket C failure. Actual outcome: PAT-003 Subtype A masked the intended PAT-005 demonstration — experience value contaminated from JV combined turnover, causing spurious experience FAIL. Output NO_BID is correct but driven by wrong reasoning. New authority: KRDC. |

## Pipeline Run

```
python scripts/run_pipeline.py \
  --pdf validation/real-tenders/Tender010.pdf \
  --profile examples/Tender-001/company-profile.json
```

| Metric | Result |
|---|---|
| Parser succeeded | Yes |
| Characters extracted | ~8,100 |
| Extraction method | stream |
| Requirements found | 4 |
| Manual edits needed | 0 |
| Recommendation generated | Yes |
| Recommendation | NO_BID |
| Expected Recommendation | BID (counterfactual without PAT-003) / NO_BID (with PAT-003 masking) |
| Qualification score | 83/100 |
| Incumbent risk | 20/100 |
| Competitive Strength | 58/100 |
| Execution Risk | 19/100 |
| Value Score | 60/100 |
| Pipeline duration | 0.011 seconds |
| Confidence | 0.87 |
| Primary Bottleneck | Experience Requirement Gap |
| Extraction mode | Offline (regex only — no ANTHROPIC_API_KEY) |
| extractor_version | v0.1.0 |
| prompt_version | 1.1.0 |
| schema_version | 1.1 |

## Failure Bucket

Bucket: B (Extraction) + C (Decision) — PAT-003 contamination created a spurious failure that drove the correct output through the wrong path

Decision Impact: **Masked** — correct recommendation (NO_BID), incorrect reasoning (experience threshold contamination, not JV structural condition)

Impact Reason: PAT-003 Subtype A contaminated the experience threshold to Rs. 40 Crore (from the JV combined turnover clause, which appears first in the document). Apex's largest project (Rs. 28.5 Crore) fails this contaminated threshold. Engine: NO_BID (experience gap). Human: NO_BID (JV mandatory — standalone categorically rejected). The intended structural eligibility failure was masked.

## Observations

**Document design and intent.** Tender010 was designed to search for a third engineering epic. The design constraints: (a) highway domain (matches Apex — eliminates PAT-001 confound), (b) JV mandatory with explicit standalone rejection, (c) all numeric thresholds individually below Apex's profile to ensure the ONLY disqualification is structural. The expected outcome was a clean Bucket C failure: engine recommends BID (all numeric thresholds pass), human says NO_BID (JV mandatory).

**What the pipeline extracted (4 requirements):**

| # | Category | Description | Threshold | Note |
|---|---|---|---|---|
| 1 | turnover | Avg Turnover ≥ Rs. 40.0 Crore (JV combined) | 40.0 INR_crores_annual | PASS — Apex 43.87 > 40 |
| 2 | turnover | Avg Turnover ≥ Rs. 20.0 Crore (Lead Partner) | 20.0 INR_crores_annual | PASS — Apex 43.87 > 20 |
| 3 | experience | 2 highway works ≥ Rs. 40.0 Crore per project | 40.0 INR_crores_per_project | FAIL — PAT-003 contamination (true threshold: Rs. 8 Crore) |
| 4 | certification | ISO 9001:2015 | — | PASS — Apex holds it |

**What was not extracted:**
- [structural] JV mandatory — standalone bids rejected — NOT EXTRACTABLE (no numeric threshold, no schema field) — PAT-005 candidate
- [financial] Net Worth ≥ Rs. 5 Crore — NOT extracted (table line-wrap: "not less\n|...|than Rs. 5 Crore" broke regex across the column boundary)
- [registration] Karnataka PWD Class-I — NOT extracted
- [entity] JV lead partner equity ≥ 51% — NOT extractable
- [entity] Each partner equity ≥ 26% — NOT extractable

**PAT-003 Subtype A interaction — the masking mechanism.**

The `_EXPERIENCE_VALUE_RE` pattern scans the full document for the first Rs. value matching `(?:value|cost|each|not\s+less\s+than).*Rs.*crore`. In the KRDC document, the JV eligibility table appears before the experience clause:

```
Document order:
  Table 1, Sl. 1: ...Combined Turnover not less than Rs. 40.00 Crore...  ← first match
  Table 2, Sl. 1: ...each of value not less than Rs. 8.00 Crore...       ← second match (ignored)

Extracted experience threshold: Rs. 40.0 Crore (contaminated from JV turnover)
True experience threshold:       Rs. 8.0 Crore
```

Apex's projects (Rs. 28.5 Cr, Rs. 14.2 Cr, Rs. 11.8 Cr) all fail Rs. 40.0 Crore → 0 matching projects → experience FAIL → NO_BID.

**Counterfactual without PAT-003.** If experience threshold had been correctly extracted as Rs. 8 Crore:
- Experience: Apex's 3 projects all > Rs. 8 Crore → PASS
- Turnover Rs. 40 Crore (JV combined): Apex 43.87 > 40 → PASS
- Turnover Rs. 20 Crore (Lead partner): PASS
- ISO 9001: PASS
- Engine: **BID** (all 4 requirements pass)
- Human: **NO_BID** (standalone bid categorically rejected — JV mandatory regardless of financial capacity)
- That would be a HIGH IMPACT Bucket C failure driven exclusively by PAT-005

**PAT-005 candidate — Structural Eligibility Condition (entity type).** The JV mandatory requirement appears four times in the document with escalating emphasis:
1. Introduction preamble: "BIDS FROM STANDALONE COMPANIES WILL NOT BE ACCEPTED"
2. Note section: standalone bids rejected per KRDC Procurement Manual 2023 Clause 4.7.2
3. Section 4.1: entity type as mandatory prerequisite, evaluated before all other criteria
4. Section 6.2: joint and several liability clause defining JV obligations

None of these triggered any extraction. The engine's `Requirement` schema has no field for entity type conditions. The engine has no concept of:
- "Is the bidder the required entity type for this tender?"
- "Does this tender require a JV, consortium, or partnership?"
- "Are there structural prerequisites before numeric thresholds apply?"

This is a design gap at the schema level, not the extraction level. Even a perfect regex extractor cannot populate a field that does not exist. A structural eligibility condition cannot be expressed as a threshold value with a unit.

**PAT-005 observed at schema level, not output level.** The output (NO_BID) happens to be correct because PAT-003 contaminated the experience value and drove a spurious FAIL. The structural eligibility gap did not produce an output-level impact in this specific tender. One additional observation where PAT-003 does not mask — i.e., the experience threshold is correctly extracted and all numeric checks pass — would demonstrate PAT-005 at the output level.

**Experience count extraction succeeded.** "at least 2 similar highway works" — no parenthetical word-form — the `_EXPERIENCE_RE` extracted count=2 correctly. This is the first tender since Tender005 where experience count extraction did not fail due to parenthetical word-forms. This confirms the root cause identified in Tenders 007, 008, 009: the "(two)" parenthetical breaks the count regex, not the count itself.

**PAT-003 Subtype A observation 4 (KRDC, fourth authority).** Pattern already promoted. New authority (KRDC), same mechanism as Tender006 (NHAI). The pattern is confirmed in a second Karnataka-based contract, different authority, same document structure (financial table appears before technical table).

**Net worth miss — table column-wrapping.** The net worth requirement spans two table rows:
```
 3  | Net Worth        | Combined Net Worth of all JV partners not less
    |                  | than Rs. 5.00 Crore as on 31 March 2026
```
The phrase "not less than" is split: "not less" ends row 1, "than Rs. 5.00 Crore" begins row 2. The `|` pipe characters between them prevent the `\s+` bridge in `not\s+less\s+than` from spanning the gap. Not yet a named pattern — a single occurrence.

**Third epic question: partial answer.** The third engineering epic candidate is **Structural Eligibility** — an entity-model gap that precedes numeric threshold evaluation (parallel to how Domain Fit precedes Qualification Fit in PAT-001). The evidence from Tender010 confirms the gap exists at the schema level. The gap did not produce an output-level impact in this instance (masked by PAT-003). RA-1 ends with PAT-005 as a candidate requiring further observation, not a promoted pattern. Two validated epics (PAT-001, PAT-003) and one candidate (PAT-005).

**Human assessment: NO_BID.**
- Entity: Apex is a standalone company — JV mandatory, standalone bid will be summarily rejected → FAIL (absolute disqualifier, evaluated before any numeric threshold)
- Domain: highway widening → road contractor → PASS (domain match)
- Turnover: Rs. 40 Crore (JV combined) → Apex 43.87 as standalone → PASS on the number, but irrelevant since JV mandate disqualifies first
- Experience: 2 highway works ≥ Rs. 8 Crore → Apex has 3 qualifying works → PASS
- Net worth Rs. 5 Crore: Apex 18.4 → PASS
- ISO 9001: PASS

## Raw Output

```
Processing: Tender010.pdf
Profile:    company-profile.json

============================================================
RECOMMENDATION: NO_BID
Qualification Score: 83/100
Competitive Strength: 58/100
Incumbent Risk: 20/100
Execution Risk: 19/100
Value Score: 57/100
Confidence: 0.87

Primary Bottleneck: Experience Requirement Gap

Reasoning:
Recommendation: NO_BID. Qualification score: 83/100. Primary issue: Experience Requirement Gap.
============================================================
```

## Extracted Requirements Detail

| # | Category | Description | Threshold | Source | Correct? |
|---|---|---|---|---|---|
| 1 | turnover | JV Combined Avg Turnover ≥ Rs. 40.0 Crore | 40.0 INR_crores_annual | Table 1, Sl. 1 | ✓ |
| 2 | turnover | Lead Partner Avg Turnover ≥ Rs. 20.0 Crore | 20.0 INR_crores_annual | Table 1, Sl. 2 | ✓ |
| 3 | experience | 2 highway works ≥ Rs. 40.0 Crore each | 40.0 INR_crores_per_project | Contaminated from Sl. 1 turnover | ✗ PAT-003 (true: Rs. 8 Crore) |
| 4 | certification | ISO 9001:2015 | — | Table 2 | ✓ |
| — | structural | JV mandatory — standalone rejected | — | Preamble + Section 4.1 | ✗ NOT extractable — PAT-005 schema gap |
| — | financial | Net Worth ≥ Rs. 5 Crore | 5.0 INR_crores | Table 1, Sl. 3 | ✗ table line-wrap broke net worth regex |
| — | registration | Karnataka PWD Class-I | — | Table 2, Sl. 3 | ✗ missed |

## RA-1 Final Pattern Status

| Pattern | Observations | Output CX | Logic CX | Status |
|---|---|---|---|---|
| PAT-001 Domain Fit | 5 | 1 (output-level) | 0 | Promoted — Epic 1 |
| PAT-003 Requirement Resolution | 4 | 0 | 0 | Promoted — Epic 2 |
| PAT-004 Identifier Extraction Miss | 2 | 0 | 0 | Observation only |
| PAT-002 Insufficient Evidence Default | 1 | 1 | 0 | Weak candidate |
| PAT-005 Structural Eligibility Condition | 1 | 0 (masked by PAT-003) | 0 | Candidate — not promoted |
