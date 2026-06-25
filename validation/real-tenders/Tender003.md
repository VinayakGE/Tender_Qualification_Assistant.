# Tender 03

## Source

| Field | Value |
|---|---|
| Portal | GitHub — dcoder01/NITA-Chatbot (real NIT, scanned OCR copy) |
| Tender ID / Reference | No.F.NITA/22(15-PUR)/2024 |
| Issuing Authority | NIT Agartala, Registrar (Purchase Section, Ministry of Education, Govt. of India) |
| Work Description | Digitization of Old Records and Provide Document Management System (Open-Source Software) for Accessing Digitized Records |
| Estimated Value | Rs. 25,00,000/- (Rs. 25 Lakhs); EMD: Rs. 1,00,000/-; Security Deposit: Rs. 5,00,000/- |
| Download URL | https://raw.githubusercontent.com/dcoder01/NITA-Chatbot/main/data/processed/pdfs/pdf_texts/Digitization_OldRecords_NITA_May2025.txt |
| Downloaded On | 2026-06-25 |
| Note | Real NIT document (OCR of scanned PDF — text quality degraded). Date of NIT: 2025. GSTIN: 16AAAGN0550K1ZG. |

## Pipeline Run

```
python scripts/run_pipeline.py \
  --pdf validation/real-tenders/Tender003.pdf \
  --profile examples/Tender-001/company-profile.json
```

| Metric | Result |
|---|---|
| Parser succeeded | Yes |
| Characters extracted | 48,171 |
| Extraction method | stream |
| Requirements found | 0 |
| Manual edits needed | 0 |
| Recommendation generated | Yes |
| Recommendation | BID |
| Expected Recommendation | NO BID (see Observations) |
| Qualification score | 100/100 |
| Incumbent risk | 20/100 |
| Pipeline duration | 0.032 seconds |
| Confidence | 0.50 (reduced — see Observations) |
| Extraction mode | Offline (regex only — no ANTHROPIC_API_KEY) |
| extractor_version | v0.1.0 |
| prompt_version | 1.1.0 |
| schema_version | 1.1 |

## Failure Bucket

Bucket: B — Extraction

The extraction is running in offline/regex mode (no API key in this environment).

Decision Impact: High

Impact Reason: The pipeline gave BID with 100/100 qualification score. The correct human assessment is NO BID. The company (Apex Infrastructure — road contractor) has zero digitization or IT service experience. The key experience requirement demands at least one completed project of scanning and indexing >25 Lakh pages for a Government organization (Section 3.6). No road construction project can satisfy this. A human reviewer would reject the company at document screening.

## Observations

**What the pipeline extracted (offline regex mode):**
- 0 requirements extracted. The regex heuristics found nothing in this tender.

**What the pipeline missed entirely:**
- Experience: at least ONE completed project of scanning/indexing >25 Lakh pages for any Govt organization — not extracted (no numeric value threshold in a form the regex recognizes; page-count metric is entirely outside the extractor's pattern vocabulary)
- Turnover: average ≥ Rs. 1 Crore (last 3 years) — not extracted (despite a numeric crore value existing; the sentence structure differed from the patterns that matched in Tender002)
- Net worth: positive net worth required — not extracted
- Financial Solvency: bank certificate ≥ Rs. 50 Lakhs — not extracted
- GST, PAN, Trade License, ITR — not extracted

**The 100/100 with zero requirements is vacuous truth.** When the extractor finds no requirements, the eligibility checker has nothing to fail against. The qualification score computes as 100/100 because zero mandatory requirements failed. This is a logical vacuity — a pass because the question was never asked.

**Confidence signal at 0.50 — partial but insufficient.** In Tender001 and Tender002 the confidence was 1.0. Here it dropped to 0.50. Inspecting the debug log: the base confidence is 0.5, and the completeness component (which rewards more requirements extracted) was 0 — so no confidence bonus was added. The engine is signalling uncertainty, but not enough to flip the recommendation. BID came out with only 50% confidence — a weak signal that is not surfaced to the user.

**Third PAT-001 observation (Subtype A — Capability Fit).** Road contractor evaluated against IT digitization services tender. Engine passed on vacuous qualification. Company cannot satisfy the scanning experience requirement regardless of turnover.

**Counterexample analysis — why this is NOT a counterexample.** The user's pre-registered counterexample definition: "a tender where the engine correctly identifies a capability-fit match/mismatch without sector-type fields." The engine did NOT correctly identify the mismatch — it recommended BID. The confidence drop (0.50) is a symptom of zero extraction, not a sector-aware signal. The engine cannot distinguish between "this company is a road contractor evaluating an IT tender" and "this is a valid IT services company evaluating an IT tender." Both would produce the same output.

**Root cause split:**
- Bucket B: 0 of ~6 requirements extracted; qualification score is vacuously 100/100
- Bucket C boundary: Even if extraction were complete, no sector-type matching logic exists; the engine would likely still pass on turnover value alone (Apex has Rs. 44 Crore turnover vs Rs. 1 Crore threshold)

## Raw Output

```
Processing: Tender003.pdf
Profile:    company-profile.json

============================================================
RECOMMENDATION: BID
Qualification Score: 100/100
Competitive Strength: 45/100
Incumbent Risk: 20/100
Execution Risk: 16/100
Value Score: 49/100
Confidence: 0.50

Reasoning:
Recommendation: BID. Qualification score: 100/100.
============================================================
```

## Extracted Requirements Detail

| # | Category | Description | Threshold | Correct? |
|---|---|---|---|---|
| — | experience | Scanning/indexing project >25 Lakh pages for Govt org | — (page count, not value) | ✗ missed |
| — | turnover | Average Annual Turnover ≥ Rs. 1 Crore (last 3 years) | 1.0 INR_crores_annual_average | ✗ missed |
| — | financial | Positive net worth | — | ✗ missed |
| — | financial | Financial Solvency certificate ≥ Rs. 50 Lakhs from bank | 0.5 INR_crores | ✗ missed |
| — | registration | GST, PAN, Trade License, ITR | — | ✗ missed |
| — | compliance | Non-blacklisting self-declaration | — | ✗ missed |
