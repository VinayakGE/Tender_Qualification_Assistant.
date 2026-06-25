# Tender 09

## Source

| Field | Value |
|---|---|
| Portal | Synthetic — RVNL e-Tender format NIT + Corrigendum No. 1 + Corrigendum No. 2 |
| Tender ID / Reference | RVNL/SZ/MYS-DIV/ROB/2026-27/003 |
| Issuing Authority | Rail Vikas Nigam Limited (RVNL), Southern Zone, Bengaluru |
| Work Description | Construction of Road Over Bridge (ROB) at Km 134+600, Mysuru–Bengaluru Rail Section (SBC–MYS Doubling Project), replacing LC Gate No. 46, Mandya District. 5-span PSC box girder bridge (120 m) + approach roads (1.2 km each side) + railway track protection works. |
| Estimated Value | Rs. 18,50,00,000/- (Rs. 18.50 Crore); EMD: Rs. 37,00,000/- |
| Download URL | Synthetic — RVNL format |
| Downloaded On | 2026-06-25 |
| Note | PAT-003 escalation test. Two corrigenda amend the same turnover threshold twice (Rs. 30 → Rs. 50 → Rs. 55 Crore) and the experience threshold once (Rs. 7.5 → Rs. 9 Crore). Tests: (a) whether multi-corrigendum accumulation exceeds Tender008's 3-version result, (b) whether PAT-003 is observed under a new authority (RVNL), (c) behaviour when the same amended value appears in both a corrigendum "prior" block and a "new" block. Domain: railway bridge / ROB construction (new for dataset). New authority: RVNL. |

## Pipeline Run

```
python scripts/run_pipeline.py \
  --pdf validation/real-tenders/Tender009.pdf \
  --profile examples/Tender-001/company-profile.json
```

| Metric | Result |
|---|---|
| Parser succeeded | Yes |
| Characters extracted | ~9,400 |
| Extraction method | stream |
| Requirements found | 7 |
| Manual edits needed | 0 |
| Recommendation generated | Yes |
| Recommendation | NO_BID |
| Expected Recommendation | NO_BID |
| Qualification score | 61/100 |
| Incumbent risk | 20/100 |
| Competitive Strength | 30/100 |
| Execution Risk | 18/100 |
| Value Score | 57/100 |
| Pipeline duration | 0.011 seconds |
| Confidence | 0.86 |
| Primary Bottleneck | Turnover Requirement Gap |
| Extraction mode | Offline (regex only — no ANTHROPIC_API_KEY) |
| extractor_version | v0.1.0 |
| prompt_version | 1.1.0 |
| schema_version | 1.1 |

## Failure Bucket

Bucket: B (Extraction) — multi-corrigendum accumulation; no decision failure

Decision Impact: **None** — correct recommendation despite extraction anomalies

Impact Reason: Engine recommended NO_BID; human assessment is NO_BID (domain mismatch AND Rs. 55 Crore threshold fails Apex 43.87 Crore). The recommendation is correct. However, the engine accumulated 5 turnover requirements from 5 document locations instead of resolving to the single authoritative value (Rs. 55 Crore, Corrigendum No. 2). Each additional corrigendum linearly grows the accumulation.

## Observations

**Document structure design.** Tender009 extends the Tender008 corrigendum stress test with a second corrigendum. Corrigendum No. 1 raised turnover Rs. 30 → Rs. 50 Crore. Corrigendum No. 2 raised it further to Rs. 55 Crore and separately raised the experience threshold Rs. 7.5 → Rs. 9 Crore. The document contains three distinct turnover values spread across five text locations: the main table (pre-updated to reflect Corr. 2), Corr. 1 "original" block, Corr. 1 "amended" block, Corr. 2 "prior" block, and Corr. 2 "amended" block.

**What the pipeline extracted (7 requirements):**

| # | Category | Description | Threshold | Source Location | Correct? |
|---|---|---|---|---|---|
| 1 | turnover | Avg Turnover ≥ Rs. 55.0 Crore | 55.0 INR_crores_annual | Main eligibility table (reflects Corr. 2) | ✓ correct |
| 2 | turnover | Avg Turnover ≥ Rs. 30.0 Crore | 30.0 INR_crores_annual | Corrigendum 1 "Original requirement" block | ✗ obsolete |
| 3 | turnover | Avg Turnover ≥ Rs. 50.0 Crore | 50.0 INR_crores_annual | Corrigendum 1 "Amended requirement" block | ✗ superseded by Corr. 2 |
| 4 | turnover | Avg Turnover ≥ Rs. 50.0 Crore | 50.0 INR_crores_annual | Corrigendum 2 "Req as per Corrigendum No. 1" block | ✗ restated-prior, superseded |
| 5 | turnover | Avg Turnover ≥ Rs. 55.0 Crore | 55.0 INR_crores_annual | Corrigendum 2 "Further amended requirement" block | ✓ correct (duplicate of #1) |
| 6 | certification | Valid ISO 9001:2015 | — | Main document | ✓ correct |
| 7 | financial | Net Worth ≥ Rs. 8.0 Crore | 8.0 INR_crores | Main document | ✓ correct |

**Failed mandatory requirements (4 of 7):** Rs. 55 Crore ×2 — FAIL (Apex 43.87 < 55). Rs. 50 Crore ×2 — FAIL (Apex 43.87 < 50). Spurious PASS on Rs. 30 Crore (Apex 43.87 > 30). ISO 9001 PASS. Net Worth PASS (Apex 18.4 > 8).

**What the pipeline missed:**
- [experience] 2 bridge/ROB works ≥ Rs. 9.0 Crore — NOT extracted
- [registration] RVNL/Railway contractor enrolment — NOT extracted
- [certification] ISO 14001:2015 — NOT extracted (PAT-004)
- GST, PAN, EPF/ESIC — NOT extracted

**PAT-003 Subtype B escalation — the key finding.** Tender008 produced 3 turnover extractions from a single corrigendum. Tender009, with two corrigenda, produced 5:

```
Document location                              Value extracted
------------------------------------------------------------
Main eligibility table (updated to Corr. 2):  Rs. 55 Crore  ← authoritative
Corrigendum 1 "Original requirement":          Rs. 30 Crore  ← obsolete
Corrigendum 1 "Amended requirement":           Rs. 50 Crore  ← superseded
Corrigendum 2 "As per Corrigendum No. 1":     Rs. 50 Crore  ← restated-prior
Corrigendum 2 "Further amended requirement":   Rs. 55 Crore  ← authoritative (duplicate)

Engine accumulated: [55, 30, 50, 50, 55]  (5 requirements)
Authoritative value: Rs. 55 Crore (Corrigendum No. 2 supersedes all)
```

The accumulation grows linearly with the number of corrigenda: 1 corrigendum → 3 extractions (Tender008); 2 corrigenda → 5 extractions (Tender009). This is structurally guaranteed by how corrigenda quote the prior requirement before stating the amendment.

**PAT-003 promotion threshold met.** Three independent observations across three tenders and three authorities (NHAI Tender006, CPWD Tender008, RVNL Tender009). The Requirement Resolution failure is not document-specific — it is architectural: the pipeline has no resolution stage.

**Experience extraction: third consecutive parenthetical failure.** "at least 2 (two) bridge or ROB works" — "(two)" breaks `_EXPERIENCE_RE`. Additionally "bridge or ROB" sits between "similar" and "works", blocking the keyword match even if count extraction had succeeded. Three consecutive tenders (007, 008, 009) have now failed experience extraction due to parenthetical word-forms of counts.

**PAT-004 second observation.** ISO 14001:2015 required in Table 1, Sl. 4 — not extracted (5-digit pattern miss, same as Tender006). Apex holds ISO 14001, so this is a latent PASS miss only. The risk crystallizes when ISO 45001 (which Apex does NOT hold) appears as a requirement.

**PAT-001 present but latent.** Railway/ROB bridge construction vs. road contractor. Engine: NO_BID (turnover failures). Human: NO_BID (domain mismatch + threshold failure). PAT-001 exists but threshold failures got there first.

**Latent risk from PAT-003 Subtype B in multi-corrigendum scenarios.** The current lucky outcome (correct value extracted alongside obsolete ones, resulting in correct FAIL) will not always hold. If a future tender's corrigenda lower a threshold to below Apex's profile, the engine would accumulate [fail, fail, pass] candidates and — because any mandatory failure → NO_BID — still recommend NO_BID. Correct BID recommendation would require knowing which value governs. Without a resolver, the engine is structurally incapable of this.

**New authority: RVNL.** Rail Vikas Nigam Limited — central government PSU under Ministry of Railways. Seventh distinct authority in the RA-1 dataset.

**Human assessment: NO_BID.**
- Domain: ROB/railway bridge construction → road contractor, zero bridge experience → FAIL
- Turnover: Rs. 55 Crore (Corr. 2) → Apex 43.87 Crore → FAIL
- Experience: 2 bridge/ROB works ≥ Rs. 9 Crore → road projects excluded → FAIL
- RVNL enrollment: Apex holds Karnataka PWD Class-I, not RVNL/Railway → FAIL
- ISO 9001: Apex holds it → PASS
- ISO 14001: Apex holds it → PASS (missed by engine)
- Net Worth Rs. 8 Crore: Apex 18.4 Crore → PASS

## Raw Output

```
Processing: Tender009.pdf
Profile:    company-profile.json

============================================================
RECOMMENDATION: NO_BID
Qualification Score: 61/100
Competitive Strength: 30/100
Incumbent Risk: 20/100
Execution Risk: 18/100
Value Score: 57/100
Confidence: 0.86

Primary Bottleneck: Turnover Requirement Gap

Reasoning:
Recommendation: NO_BID. Qualification score: 61/100. Primary issue: Turnover Requirement Gap.
============================================================
```

## Extracted Requirements Detail

| # | Category | Description | Threshold | Source | Correct? |
|---|---|---|---|---|---|
| 1 | turnover | Avg Turnover ≥ Rs. 55.0 Crore | 55.0 INR_crores_annual | Main table | ✓ |
| 2 | turnover | Avg Turnover ≥ Rs. 30.0 Crore | 30.0 INR_crores_annual | Corr. 1 "Original" | ✗ obsolete |
| 3 | turnover | Avg Turnover ≥ Rs. 50.0 Crore | 50.0 INR_crores_annual | Corr. 1 "Amended" | ✗ superseded |
| 4 | turnover | Avg Turnover ≥ Rs. 50.0 Crore | 50.0 INR_crores_annual | Corr. 2 "As per Corr. 1" | ✗ restated-prior |
| 5 | turnover | Avg Turnover ≥ Rs. 55.0 Crore | 55.0 INR_crores_annual | Corr. 2 "Further amended" | ✓ duplicate |
| 6 | certification | ISO 9001:2015 | — | Main document | ✓ |
| 7 | financial | Net Worth ≥ Rs. 8.0 Crore | 8.0 INR_crores | Main document | ✓ |
| — | experience | 2 bridge/ROB works ≥ Rs. 9.0 Crore | 9.0 INR_crores | Main table + Corr. 2 | ✗ missed — "(two)" + "bridge" domain noun |
| — | certification | ISO 14001:2015 | — | Main document | ✗ missed — PAT-004 |
| — | registration | RVNL/Railway enrolment | — | Main document | ✗ missed |

## PAT-003 Log After Tender009

| # | Tender | Subtype | Accumulation | Authoritative | Versions | Decision Impact |
|---|---|---|---|---|---|---|
| 1 | Tender006 (NHAI) | A — Cross-Contamination | Experience ← Turnover value | Rs. 75 Cr | 2 candidates | None |
| 2 | Tender008 (CPWD) | B — Version Accumulation | [25, 25, 50] | Rs. 50 Cr | 3 candidates | None |
| 3 | Tender009 (RVNL) | B — Version Accumulation | [55, 30, 50, 50, 55] | Rs. 55 Cr | 5 candidates | None |

PAT-003: **3 observations | Promotion threshold met** | Engineering: queued for post-RA-1
