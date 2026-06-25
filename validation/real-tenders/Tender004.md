# Tender 04

## Source

| Field | Value |
|---|---|
| Portal | GitHub — Vyom-Agrawal/suddridh (synthetic NIT for software testing) |
| Tender ID / Reference | CRPF/DG/PROC/2025-26/MOCK-001 |
| Issuing Authority | Central Reserve Police Force (CRPF), Directorate General, New Delhi |
| Work Description | Supply, Installation and Commissioning of Integrated Communication Infrastructure for CRPF Sector Offices |
| Estimated Value | Rs. 45,00,00,000/- (Rs. 45 Crore); EMD: Rs. 90,00,000/- |
| Download URL | https://raw.githubusercontent.com/Vyom-Agrawal/suddridh/main/data/mock_documents/tender_MOCK001.txt |
| Downloaded On | 2026-06-25 |
| Note | Synthetic document (labeled MOCK-001). Compact but structurally complete — sections 1, 3, 5 and Annexure I. 4,418 chars, 2 pages. |

## Pipeline Run

```
python scripts/run_pipeline.py \
  --pdf validation/real-tenders/Tender004.pdf \
  --profile examples/Tender-001/company-profile.json
```

| Metric | Result |
|---|---|
| Parser succeeded | Yes |
| Characters extracted | 4,384 |
| Extraction method | stream |
| Requirements found | 5 |
| Manual edits needed | 0 |
| Recommendation generated | Yes |
| Recommendation | BID |
| Expected Recommendation | NO BID (see Observations) |
| Qualification score | 100/100 |
| Incumbent risk | 20/100 |
| Competitive Strength | 73/100 |
| Pipeline duration | 0.009 seconds |
| Confidence | 1.00 |
| Extraction mode | Offline (regex only — no ANTHROPIC_API_KEY) |
| extractor_version | v0.1.0 |
| prompt_version | 1.1.0 |
| schema_version | 1.1 |

## Failure Bucket

Bucket: B/C boundary — Extraction and Decision

Decision Impact: High

Impact Reason: The pipeline gave BID with 100/100 qualification score and full confidence (1.0). The correct human assessment is NO BID. The company (Apex Infrastructure — road contractor) has zero communication infrastructure experience and lacks OHSAS 18001 / ISO 45001 certification. A bidder without communication/networking project experience would fail the technical evaluation immediately — the experience requirement explicitly states "communication or networking equipment for government organizations."

## Observations

**What the pipeline extracted (offline regex mode):**
1. [turnover] Annual Turnover ≥ Rs. 15 Crore — CORRECT threshold (extracted twice, duplicate)
2. [turnover] Annual Turnover ≥ Rs. 15 Crore — CORRECT threshold (duplicate of #1)
3. [experience] 3 similar projects ≥ Rs. 10 Crore — CORRECT value and count
4. [certification] ISO 9001 — CORRECT
5. [certification] ISO 9001:2015 — CORRECT (duplicate of #4)

**What the pipeline missed entirely:**
- OHSAS 18001 / ISO 45001 certification requirement — not extracted (not in regex vocabulary)
- GST, PAN, EPF/ESI registration requirements — not extracted

**The most important observation in Tender004:** The experience checker found 3 matching projects and returned PASS. Those projects were: NH-48 road widening (Rs. 28.5 Cr), Urban Roads Pune (Rs. 14.2 Cr), MP State Highway (Rs. 11.8 Cr). All three exceed the Rs. 10 Crore threshold. But none of them involve communication or networking equipment — they are road construction projects. The eligibility checker verified *value and count* only; it never inspected project type. The domain mismatch is invisible to it.

**This is PAT-001's sharpest illustration yet.** Previous tenders showed a path: the extractor missed the experience requirement → the eligibility checker had nothing to fail → vacuously passed. Here the experience requirement *was* extracted correctly (value/count), and the eligibility checker *was* invoked — and it still passed, because it evaluated the wrong dimension. The failure is now unambiguously in the eligibility logic (Bucket C), not just in extraction (Bucket B).

**Duplicate extraction.** Turnover and ISO 9001 were each extracted twice from the Annexure I compliance checklist and the main criteria section. The deduplication logic is missing. This inflates the mandatory requirement count (5 instead of 3) and produces a misleading "5 of 5 verified" confidence signal.

**PAT-002 not present.** 5 requirements extracted, confidence = 1.0. This tender does not exhibit the insufficient-evidence pattern.

**Counterexample analysis — why this is NOT a counterexample to PAT-001.** The engine recommends BID. PAT-001 is confirmed again. The experience checker's domain-blind pass is the clearest evidence yet that domain compatibility is not evaluated anywhere in the pipeline.

**Root cause split:**
- Bucket B: 2 missing requirements (OHSAS, registrations); 2 duplicate extractions
- Bucket C: eligibility checker passed road construction projects against a communication/networking experience requirement — value matched, domain not checked

## Raw Output

```
Processing: Tender004.pdf
Profile:    company-profile.json

============================================================
RECOMMENDATION: BID
Qualification Score: 100/100
Competitive Strength: 73/100
Incumbent Risk: 20/100
Execution Risk: 13/100
Value Score: 63/100
Confidence: 1.00

Reasoning:
Recommendation: BID. Qualification score: 100/100.
============================================================
```

## Extracted Requirements Detail

| # | Category | Description | Threshold | Correct? |
|---|---|---|---|---|
| 1 | turnover | Annual Turnover ≥ Rs. 15 Crore (each of last 3 FYs) | 15.0 INR_crores_annual | ✓ correct value |
| 2 | turnover | Annual Turnover ≥ Rs. 15 Crore (each of last 3 FYs) | 15.0 INR_crores_annual | ✗ duplicate of #1 |
| 3 | experience | 3 similar projects ≥ Rs. 10 Crore (communication/networking) | 10.0 INR_crores_per_project, count≥3 | ✓ value/count correct — ✗ domain not captured |
| 4 | certification | ISO 9001 | — | ✓ correct |
| 5 | certification | ISO 9001:2015 | — | ✗ duplicate of #4 |
| — | certification | OHSAS 18001 / ISO 45001 | — | ✗ missed |
| — | registration | GST, PAN, EPF/ESI | — | ✗ missed |
