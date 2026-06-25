# Tender 01

## Source

| Field | Value |
|---|---|
| Portal | GitHub — nabro356/TenderSight (synthetic NIT for software testing) |
| Tender ID / Reference | CRPF/EW/2025-26/BOP-RAJ/0042 |
| Issuing Authority | Central Reserve Police Force (CRPF), Engineering Wing, New Delhi |
| Work Description | Construction of 06 Border Outpost Buildings in Rajasthan Sector (Barmer & Jaisalmer Districts) |
| Estimated Value | Rs. 18,50,00,000/- (Rs. 18.5 Crore) |
| Download URL | https://raw.githubusercontent.com/nabro356/TenderSight/835b07ed2f376e08bccbfcbe0c176be3b378f7df/sample_bundle/tender_bundle/RFP_NIT_Border_Outpost_Construction.txt |
| Downloaded On | 2026-06-25 |
| Note | Synthetic document created for testing. Includes NIT + ATC + Corrigendum (3 documents merged into one PDF). |

## Pipeline Run

```
python scripts/run_pipeline.py \
  --pdf validation/real-tenders/Tender001.pdf \
  --profile examples/Tender-001/company-profile.json
```

| Metric | Result |
|---|---|
| Parser succeeded | Yes |
| Characters extracted | 11,638 |
| Extraction method | stream |
| Requirements found | 4 |
| Manual edits needed | 0 |
| Recommendation generated | Yes |
| Recommendation | BID |
| Expected Recommendation | REVIEW (see Observations) |
| Qualification score | 100/100 |
| Incumbent risk | 20/100 |
| Pipeline duration | 0.015 seconds |
| Extraction mode | Offline (regex only — no ANTHROPIC_API_KEY) |
| extractor_version | v0.1.0 |
| prompt_version | 1.1.0 |
| schema_version | 1.1 |

## Failure Bucket

Bucket: B — Extraction

The extraction is running in offline/regex mode (no API key in this environment).

Decision Impact: High

Impact Reason: The pipeline gave BID with 100/100 qualification score. The correct human assessment is REVIEW. The company (Apex Infrastructure — road contractor) does not have the experience type required (construction of government/defense *buildings*). A wrong BID recommendation here means the bidder submits a Rs. 18.5 Crore bid that will be rejected at the technical evaluation stage — wasted bid preparation cost and credibility risk.

## Observations

**What the pipeline extracted (offline regex mode):**
1. [turnover] Average Annual Turnover ≥ Rs. 5.0 Crore — CORRECT value, but duplicated (matched twice from NIT and ATC text)
2. [experience] 2 similar works, each ≥ Rs. 5.0 Crore — WRONG value (actual is Rs. 7 Crore each, or Rs. 12 Crore single)
3. [certification] Valid ISO 9001:2015 — CORRECT

**What the pipeline missed entirely:**
- Net worth: positive net worth required (Section 2.1.2) — not extracted
- Solvency certificate: Rs. 3 Crore from a Scheduled Bank (Section 2.1.3) — not extracted
- CPWD/MES/PWD Class-I registration (Section 2.3.1) — not extracted
- Contract Labour License (Section 2.3.2) — not extracted
- ATC revision: turnover revised from Rs. 5 Crore to Rs. 4 Crore (ATC-7) — not extracted
- Desert/arid region experience requirement (ATC-1) — not extracted
- Experience sector type: "construction of government/defense buildings" — not extracted (regex can't classify sector)

**The critical failure:** The experience requirement is for *building construction* (BOP structures). The company's profile shows three completed projects — all road construction (NH-48, Urban Roads, MP State Highway). The pipeline's eligibility checker evaluated experience on value (28.5 Cr, 14.2 Cr, 11.8 Cr — all exceed Rs. 5 Crore threshold), so it returned PASS. A human reviewer would immediately flag the sector mismatch.

**Root cause split:**
- Bucket B: Regex extraction missed 5 of 8 requirements; extracted wrong experience value; produced a duplicate requirement
- Bucket C boundary: Even if extraction were complete, the engine has no sector-type matching logic to catch road-vs-building mismatch

**On the corrigendum:** The ATC-7 amended turnover from 5 Crore to 4 Crore. The pipeline processed both documents as a single merged text and picked up the Rs. 5 Crore mention. The corrigendum supersession was not detected (Bucket B — multi-document corrigendum handling not implemented).

## Raw output

```
Processing: Tender001.pdf
Profile:    company-profile.json

============================================================
RECOMMENDATION: BID
Qualification Score: 100/100
Competitive Strength: 75/100
Incumbent Risk: 20/100
Execution Risk: 13/100
Value Score: 59/100
Confidence: 1.00

Reasoning:
Recommendation: BID. Qualification score: 100/100.
============================================================
```

## Extracted Requirements Detail

| # | Category | Description | Threshold | Correct? |
|---|---|---|---|---|
| 1 | turnover | AAT ≥ Rs. 5.0 Crore (last 3 years) | 5.0 INR_crores_annual_average | ✓ value correct (ATC revision to 4 Cr missed) |
| 2 | turnover | AAT ≥ Rs. 5.0 Crore (last 3 years) | 5.0 INR_crores_annual_average | ✗ duplicate |
| 3 | experience | 2 similar works ≥ Rs. 5.0 Crore each | 5.0 INR_crores_per_project | ✗ wrong value (actual Rs. 7 Crore); sector type not captured |
| 4 | certification | ISO 9001:2015 | — | ✓ correct |
| — | financial | Net worth positive (2.1.2) | — | ✗ missed |
| — | financial | Solvency certificate Rs. 3 Crore (2.1.3) | — | ✗ missed |
| — | technical | CPWD/MES/PWD Class-I registration (2.3.1) | — | ✗ missed |
| — | technical | Contract Labour License (2.3.2) | — | ✗ missed |
| — | technical | Desert/arid experience (ATC-1) | — | ✗ missed |
