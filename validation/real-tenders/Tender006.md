# Tender 06

## Source

| Field | Value |
|---|---|
| Portal | Synthetic — NHAI-format NIT constructed to test threshold-failure detection |
| Tender ID / Reference | NHAI/RO-KGO/NH-66/HC-03/2026-27/01 |
| Issuing Authority | National Highways Authority of India (NHAI), Regional Office Karnataka & Goa |
| Work Description | Construction of 4-Lane Divided Carriageway on NH-66 (Panaji–Udupi, Package HC-03), Chainage Km 182.000 to Km 231.600 (49.6 km) |
| Estimated Value | Rs. 4,50,00,00,000/- (Rs. 450 Crore); EMD: Rs. 90,00,000/- |
| Download URL | Synthetic (NHAI-format, structured to match regex extractor vocabulary) |
| Downloaded On | 2026-06-25 |
| Note | Diagnostic tender. Domain: road/highway (matches Apex). Thresholds deliberately set above Apex's profile: turnover Rs. 150 Cr (Apex avg 43.87 Cr), experience Rs. 75 Cr per project (Apex max 28.5 Cr), net worth Rs. 50 Cr (Apex 18.4 Cr). Tests whether qualification logic correctly fails Apex when domain is not the confound. |

## Pipeline Run

```
python scripts/run_pipeline.py \
  --pdf validation/real-tenders/Tender006.pdf \
  --profile examples/Tender-001/company-profile.json
```

| Metric | Result |
|---|---|
| Parser succeeded | Yes |
| Characters extracted | 8,476 |
| Extraction method | stream |
| Requirements found | 4 |
| Manual edits needed | 0 |
| Recommendation generated | Yes |
| Recommendation | NO_BID |
| Expected Recommendation | NO_BID (see Observations) |
| Qualification score | 50/100 |
| Incumbent risk | 20/100 |
| Competitive Strength | 20/100 |
| Execution Risk | 25/100 |
| Value Score | 56/100 |
| Pipeline duration | 0.011 seconds |
| Confidence | 0.92 |
| Primary Bottleneck | Turnover Requirement Gap |
| Extraction mode | Offline (regex only — no ANTHROPIC_API_KEY) |
| extractor_version | v0.1.0 |
| prompt_version | 1.1.0 |
| schema_version | 1.1 |

## Failure Bucket

Bucket: B (Extraction) — partial; no decision failure

Decision Impact: **None** — correct recommendation despite extraction errors

Impact Reason: Engine recommended NO_BID; human assessment is NO_BID. The recommendation is correct. Three mandatory requirements correctly failed (turnover, experience, net worth). However, the experience threshold was extracted with the wrong value (Rs. 150 Crore instead of Rs. 75 Crore — cross-contaminated from the turnover clause). The FAIL outcome is unchanged (28.5 < 150 is still a fail), but the extracted threshold is wrong. Additionally, ISO 14001:2015 and ISO 45001:2018 were not extracted (5-digit ISO cert regex miss).

## Observations

**Diagnostic design.** This is the first tender designed to answer a specific question: does the qualification logic correctly produce NO_BID when the company is in the right domain but fails numeric thresholds? Tender001–004 all failed on domain mismatch. Tender005 was domain-matched but with low thresholds Apex easily cleared. Tender006 is domain-matched with thresholds Apex cannot meet.

**What the pipeline extracted:**
1. [turnover] Annual Turnover ≥ Rs. 150.0 Crore (3-year avg) — CORRECT threshold
2. [experience] 2 similar works, each ≥ Rs. 150.0 Crore — WRONG value (cross-contamination; should be Rs. 75 Crore)
3. [certification] ISO 9001:2015 — CORRECT
4. [financial] Net Worth ≥ Rs. 50.0 Crore — CORRECT threshold

**What the pipeline missed:**
- [certification] ISO 14001:2015 — not extracted (5-digit ISO cert numbers not captured by `_ISO_RE`)
- [certification] ISO 45001:2018 — not extracted (same reason)
- [registration] NHAI Class-I empanelment, GST, PAN, EPF/ESIC — not extracted

**How each requirement was evaluated:**
1. Turnover: 43.87 Crore avg < 150.0 Crore threshold → FAIL (mandatory) ← correct
2. Experience: max project 28.5 Crore < 150.0 Crore threshold → FAIL (mandatory) ← FAIL for wrong threshold, but same outcome
3. ISO 9001:2015: Apex holds this cert → PASS
4. Net Worth: 18.4 Crore < 50.0 Crore → FAIL (mandatory)

**Failed mandatory requirements: 3 of 4.** Qualification score: 50/100.

**Engine recommendation: NO_BID. Human assessment: NO_BID.** This is the first correct NO_BID from qualification logic — and the first tender where the engine's failure mode is not PAT-001.

**PAT-001 not triggered.** Domain is road/highway — matches Apex's profile. The engine did not need to detect domain fit; the threshold checks alone were sufficient to produce the correct answer. This confirms that PAT-001 is specifically about domain-mismatched tenders where BID is wrong. When domain matches and thresholds clearly fail, the qualification logic works.

**New Bucket B observation — Experience Value Cross-Contamination.** The `_EXPERIENCE_VALUE_RE` regex matches the first occurrence of "value not less than Rs. [amount] Crore" in the document. In Tender006, the turnover clause ("Annual Turnover not less than Rs. 150.00 Crore") appeared before the experience clause ("each not less than Rs. 75.00 Crore"). The regex matched the turnover clause first. The experience threshold was therefore extracted as Rs. 150.0 Crore instead of Rs. 75.0 Crore. This is a structural bug in the regex extraction — the experience value extractor has no proximity constraint to the experience clause.

**New Bucket B observation — 5-digit ISO cert regex miss.** The `_ISO_RE` pattern `\bISO\s+(\d{4}(?:[-:]\d{4})?)\b` matches 4-digit ISO numbers (9001, 9002, etc.) but not 5-digit numbers (14001, 45001). ISO 14001:2015 and ISO 45001:2018 are both unextractable by the current regex. Apex holds ISO 14001:2015 (PASS if extracted), but does not hold ISO 45001:2018 (FAIL if extracted). The hidden ISO 45001 failure is not a decision impact here because NO_BID is already correct from turnover/net worth alone — but in a future tender where ISO 45001 is the only failing requirement, this miss would change the recommendation from NO_BID to BID.

**Human assessment of missed requirements:**
- ISO 14001:2015: Apex holds it → PASS (hidden pass, no impact on decision)
- ISO 45001:2018: Apex does NOT hold it → FAIL (hidden fail — but NO_BID is already correct)
- NHAI empanelment: Apex completed NH-48 for NHAI but NHAI Class-I empanelment status unknown → uncertain (not assessed)

**PAT-002 not present.** 4 requirements extracted, confidence = 0.92 — not a vacuous-pass scenario.

## Raw Output

```
Processing: Tender006.pdf
Profile:    company-profile.json

============================================================
RECOMMENDATION: NO_BID
Qualification Score: 50/100
Competitive Strength: 20/100
Incumbent Risk: 20/100
Execution Risk: 25/100
Value Score: 56/100
Confidence: 0.92

Primary Bottleneck: Turnover Requirement Gap

Reasoning:
Recommendation: NO_BID. Qualification score: 50/100. Primary issue: Turnover Requirement Gap.
============================================================
```

## Extracted Requirements Detail

| # | Category | Description | Threshold | Correct? |
|---|---|---|---|---|
| 1 | turnover | Annual Turnover ≥ Rs. 150.0 Crore (last 3 FYs) | 150.0 INR_crores_annual_average | ✓ correct |
| 2 | experience | 2 similar works, each ≥ Rs. 150.0 Crore | 150.0 INR_crores_per_project | ✗ wrong value — should be 75.0 (cross-contaminated from turnover clause) |
| 3 | certification | ISO 9001:2015 | — | ✓ correct |
| 4 | financial | Net Worth ≥ Rs. 50.0 Crore | 50.0 INR_crores | ✓ correct |
| — | certification | ISO 14001:2015 | — | ✗ missed (5-digit cert, regex `_ISO_RE` only captures \d{4}) |
| — | certification | ISO 45001:2018 | — | ✗ missed (same reason) |
| — | registration | NHAI Class-I empanelment, GST, PAN, EPF/ESIC | — | ✗ missed |

## RA-1 Diagnostic Value

**Question asked:** Can the qualification logic correctly fail Apex on numeric thresholds when domain is not the confound?

**Answer:** Yes. Three mandatory failures correctly identified (turnover, experience, net worth). NO_BID is correct.

**What this means for the pattern register:**
- PAT-001 bounded: the engine's threshold logic does work; it fails specifically when domain mismatch is present and thresholds alone are insufficient to detect the mismatch
- Extraction has two newly documented failure modes: experience value cross-contamination (Bucket B) and 5-digit ISO cert miss (Bucket B)
- A new latent risk is identified: if ISO 45001:2018 were the ONLY disqualifying requirement in a future tender, the engine would miss it and recommend BID incorrectly

**No new pattern promoted.** The extraction bugs are Bucket B observations consistent with the known regex coverage gap. A new pattern would require the extraction failure to cause a decision failure — here it does not.

**New authority: NHAI (central).** Previous tenders: CRPF, NIT Agartala (×2), BBMP (×2). NHAI is the first central infrastructure authority in the dataset. Domain: road/highway.
