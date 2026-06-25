# Tender 08

## Source

| Field | Value |
|---|---|
| Portal | Synthetic — CPWD e-Tender format NIT + Corrigendum No. 1 |
| Tender ID / Reference | CPWD/KAR-CRC/KVS-BNG-01/2026-27 |
| Issuing Authority | Central Public Works Department (CPWD), Karnataka Circle, Bengaluru |
| Work Description | Construction of Kendriya Vidyalaya School Complex (Admin Block G+2 + Academic Block G+3 + 16 Staff Quarters), Sadashivanagar, Bengaluru. Estimated cost Rs. 11.80 Crore, Kendriya Vidyalaya Sangathan project. |
| Estimated Value | Rs. 11,80,00,000/- (Rs. 11.80 Crore); EMD: Rs. 23,60,000/- |
| Download URL | Synthetic — CPWD format |
| Downloaded On | 2026-06-25 |
| Note | Document structure stress test. Eligibility in tabular format. Corrigendum No. 1 amends Annual Turnover threshold upward from Rs. 25 Crore to Rs. 50 Crore. Tests: (a) tabular extraction, (b) corrigendum handling, (c) behaviour when conflicting threshold values exist in the same document. Domain: institutional building construction (new for this dataset). New authority: CPWD (central). |

## Pipeline Run

```
python scripts/run_pipeline.py \
  --pdf validation/real-tenders/Tender008.pdf \
  --profile examples/Tender-001/company-profile.json
```

| Metric | Result |
|---|---|
| Parser succeeded | Yes |
| Characters extracted | ~8,900 |
| Extraction method | stream |
| Requirements found | 5 |
| Manual edits needed | 0 |
| Recommendation generated | Yes |
| Recommendation | NO_BID |
| Expected Recommendation | NO_BID (see Observations) |
| Qualification score | 86/100 |
| Incumbent risk | 20/100 |
| Competitive Strength | 50/100 |
| Execution Risk | 16/100 |
| Value Score | 60/100 |
| Pipeline duration | 0.010 seconds |
| Confidence | 0.90 |
| Primary Bottleneck | Turnover Requirement Gap |
| Extraction mode | Offline (regex only — no ANTHROPIC_API_KEY) |
| extractor_version | v0.1.0 |
| prompt_version | 1.1.0 |
| schema_version | 1.1 |

## Failure Bucket

Bucket: B (Extraction) — structural document stress; no decision failure

Decision Impact: **None** — correct recommendation despite extraction anomalies

Impact Reason: Engine recommended NO_BID; human assessment is NO_BID (both for domain mismatch AND threshold failure). The recommendation is correct. However, the path to NO_BID is structurally unsound: the engine accumulated three turnover extractions (two wrong, one right) rather than resolving to the corrigendum-amended value.

## Observations

**Document structure design.** Tender008 was designed to stress two aspects of document parsing: (1) tabular eligibility format, and (2) corrigendum with amended threshold. The original NIT set Annual Turnover at Rs. 25 Crore; Corrigendum No. 1 raised it to Rs. 50 Crore. Apex's turnover (43.87 Crore) passes the original but fails the corrigendum-amended threshold. This design isolates the question: does the pipeline correctly read the amended value?

**What the pipeline extracted (5 requirements):**
1. [turnover] Rs. 25.0 Crore (3-year avg) — from main table (Table 1, Sl. 1) → PASS (Apex 43.87 Cr > 25 Cr)
2. [turnover] Rs. 25.0 Crore (3-year avg) — from corrigendum "Original requirement" text → PASS (duplicate)
3. [turnover] Rs. 50.0 Crore (3-year avg) — from corrigendum "Amended requirement" text → FAIL (Apex 43.87 Cr < 50 Cr)
4. [certification] ISO 9001:2015 → PASS
5. [financial] Net Worth ≥ Rs. 5.0 Crore → PASS (Apex 18.4 Crore)

**What the pipeline missed:**
- [experience] 2 similar institutional building works ≥ Rs. 5.0 Crore — NOT extracted
- [registration] CPWD Class I / Special Class registration — NOT extracted
- GST, PAN, EPF/ESIC — NOT extracted

**Corrigendum accumulation (PAT-003 observation 2).** The keyword "Annual Turnover" appears three times in the document: once in the main eligibility table, once in the corrigendum "Original requirement" text, and once in the corrigendum "Amended requirement" text. `_TURNOVER_RE` uses `finditer` with no deduplication, so all three match. The engine accumulated three separate turnover requirements instead of identifying that the corrigendum supersedes the original. The requirements are:
- Rs. 25 Crore (spurious, from table) — 1 match
- Rs. 25 Crore (spurious, from corrigendum "Original") — 1 match (duplicate of the pre-amendment value)
- Rs. 50 Crore (the correct, current requirement from corrigendum "Amended") — 1 match

The engine happened to extract the correct corrigendum value alongside two obsolete ones. The NO_BID recommendation was driven by the Rs. 50 Crore failure. But the engine has no mechanism to know WHICH of the three is authoritative.

**Latent risk from PAT-003 in corrigendum scenarios.** If the corrigendum had LOWERED the threshold (instead of raising it) and the engine extracted only the original (higher) value, it would have recommended NO_BID incorrectly. Conversely, if only the pre-corrigendum value were extracted and it happened to pass, BID would be recommended when the corrigendum-raised threshold actually fails. The current lucky outcome (Rs. 50 Crore extracted alongside the two Rs. 25 Crore extractions) is not reliable.

**Experience requirement not extracted — new Bucket B signal.** The experience clause in the table reads "Successfully completed at least 2 (two) similar institutional or government building construction works, each of value not less than Rs. 5.00 Crore." The `_EXPERIENCE_RE` pattern requires the count followed immediately by `(?:similar\s+)?(?:works?|projects?|road|highway)`. In this text, after "2 (two)" comes " similar\n    institutional or government building construction\n    works". The "(two)" parenthetical breaks the count match (same failure as Tender007's "(one)"). Even without the parenthetical, "institutional or government building construction works" would require the engine to find "works" many tokens after "similar" — the intermediate nouns break the pattern.

This is the second consecutive tender where a parenthetical word-form of a number breaks experience extraction. Combined with Tender007 (where "canal" broke keyword matching), the experience regex is now documented as fragile to any natural-language elaboration of the experience clause.

**PAT-001 (domain mismatch).** Road contractor vs institutional building construction. Engine: NO_BID (driven by Rs. 50 Crore threshold fail). Human: NO_BID (driven by domain mismatch AND threshold fail). The domain mismatch is present but was not the determining factor for the engine's decision in this tender — the threshold fail got there first. PAT-001 is present but latent: had the corrigendum not raised the turnover, the engine would have recommended BID (turnover PASS, experience not extracted → vacuous pass) while human says NO BID (building experience required).

**PAT-002 not present.** 5 requirements extracted, albeit messily.

**New authority: CPWD.** Central Public Works Department — a major central government engineering body. Distinct from CRPF, NIT Agartala, BBMP, NHAI, CNNL.

**Human assessment: NO_BID.**
- Domain: institutional building construction → Apex road contractor, zero building experience → FAIL
- Turnover: Rs. 50 Crore (per corrigendum) → Apex 43.87 Crore → FAIL
- Experience: institutional/government building works required; road construction explicitly excluded → FAIL
- CPWD registration: Apex holds Karnataka PWD Class-I, not CPWD Class-I → FAIL
- Net worth Rs. 5 Crore: Apex 18.4 Crore → PASS (only passing criterion)

## Raw Output

```
Processing: Tender008.pdf
Profile:    company-profile.json

============================================================
RECOMMENDATION: NO_BID
Qualification Score: 86/100
Competitive Strength: 50/100
Incumbent Risk: 20/100
Execution Risk: 16/100
Value Score: 60/100
Confidence: 0.90

Primary Bottleneck: Turnover Requirement Gap

Reasoning:
Recommendation: NO_BID. Qualification score: 86/100. Primary issue: Turnover Requirement Gap.
============================================================
```

## Extracted Requirements Detail

| # | Category | Description | Threshold | Source | Correct? |
|---|---|---|---|---|---|
| 1 | turnover | Avg Turnover ≥ Rs. 25.0 Crore | 25.0 INR_crores_annual | Main eligibility table | ✗ obsolete (corrigendum superseded) |
| 2 | turnover | Avg Turnover ≥ Rs. 25.0 Crore | 25.0 INR_crores_annual | Corrigendum "Original" text | ✗ spurious duplicate of pre-amendment value |
| 3 | turnover | Avg Turnover ≥ Rs. 50.0 Crore | 50.0 INR_crores_annual | Corrigendum "Amended" text | ✓ correct current requirement |
| 4 | certification | ISO 9001:2015 | — | Main document | ✓ correct |
| 5 | financial | Net Worth ≥ Rs. 5.0 Crore | 5.0 INR_crores | Main document | ✓ correct |
| — | experience | 2 building works ≥ Rs. 5.0 Crore | 5.0 INR_crores_per_project | Main table | ✗ missed — "(two)" parenthetical breaks count extraction |
| — | registration | CPWD Class I Contractor | — | Main document | ✗ missed |

## PAT-003 Log After Tender008

| # | Tender | Contamination Type | Extracted (Wrong) | Correct Value | Decision Impact |
|---|---|---|---|---|---|
| 1 | Tender006 (NHAI) | Turnover→Experience value | Rs. 150 Cr (from turnover) | Rs. 75 Cr | None (both fail) |
| 2 | Tender008 (CPWD) | Corrigendum accumulation | Rs. 25 Cr ×2 (obsolete) | Rs. 50 Cr | None (correct value also extracted) |

PAT-003: 2 observations | Promotion threshold not met | Engineering: None
