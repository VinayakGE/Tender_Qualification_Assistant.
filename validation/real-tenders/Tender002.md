# Tender 02

## Source

| Field | Value |
|---|---|
| Portal | GitHub — dcoder01/NITA-Chatbot (real NIT, scanned OCR copy) |
| Tender ID / Reference | NIT No. 123/NITA/Estate Elect./2023-24 |
| Issuing Authority | NIT Agartala, Registrar (Estate & Electrical Division) |
| Work Description | Comprehensive Annual Maintenance Contract for 05 (Five) numbers of Otis make Passenger lifts installed at NIT Agartala campus |
| Estimated Value | Not stated in NIT text (BOQ in separate XLS); EMD: Rs. 28,300/- |
| Contract Period | 3 years initially, extendable to 4th and 5th year on satisfactory performance |
| Download URL | https://raw.githubusercontent.com/dcoder01/NITA-Chatbot/main/data/processed/pdfs/pdf_texts/OTISTD_Nov24.txt |
| Downloaded On | 2026-06-25 |
| Note | Real NIT document (OCR of scanned PDF — text quality degraded). Bid deadline 14/12/2024; opening 16/12/2024. |

## Pipeline Run

```
python scripts/run_pipeline.py \
  --pdf validation/real-tenders/Tender002.pdf \
  --profile examples/Tender-001/company-profile.json
```

| Metric | Result |
|---|---|
| Parser succeeded | Yes |
| Characters extracted | 76,248 |
| Extraction method | stream |
| Requirements found | 1 |
| Manual edits needed | 0 |
| Recommendation generated | Yes |
| Recommendation | BID |
| Expected Recommendation | NO BID (see Observations) |
| Qualification score | 100/100 |
| Incumbent risk | 60/100 |
| Pipeline duration | 0.048 seconds |
| Extraction mode | Offline (regex only — no ANTHROPIC_API_KEY) |
| extractor_version | v0.1.0 |
| prompt_version | 1.1.0 |
| schema_version | 1.1 |

## Failure Bucket

Bucket: B — Extraction

The extraction is running in offline/regex mode (no API key in this environment).

Decision Impact: High

Impact Reason: The pipeline gave BID with 100/100 qualification score. The correct human assessment is NO BID (stronger than Tender001's REVIEW). The company (Apex Infrastructure — road contractor) cannot qualify for an Otis Lift AMC tender because: (1) they have zero lift maintenance experience, (2) they cannot obtain an OEM certificate from Otis Elevators (required by Section 8 of the NIT), and (3) they have no Lift AMC works in the past 3 years. This is not a borderline case — the company would be rejected at document screening before technical evaluation begins.

## Observations

**What the pipeline extracted (offline regex mode):**
1. [turnover] Average Annual Turnover ≥ Rs. 25 Lakhs — CORRECT value and threshold

**What the pipeline missed entirely:**
- Lift AMC experience: experience in successfully completed Lift AMC works during last 3 years — not extracted (no value threshold to match; experience type not captured)
- OEM certificate: Certificate from Otis manufacturer certifying bidder as authorized representative/dealer/vendor — not extracted (this is a hard disqualifier; no regex pattern for manufacturer authorization)
- Firm registration certificate — not extracted
- Non-blacklisting declaration — not extracted
- PAN and GST registration — not extracted

**The critical failure:** The experience requirement is for *Lift Annual Maintenance Contract* work. The company profile shows three completed projects — all road construction (NH-48, Urban Roads Pune, MP State Highway). Not a single lift-related project. The pipeline's eligibility checker evaluated only the one extracted requirement (turnover: 43.87 Crore > 0.25 Crore threshold), returned PASS, and recommended BID with 100/100. A human reviewer would immediately recognize this as an impossible qualification.

**OEM certificate as a hard disqualifier:** The NIT explicitly requires "Certificate from the Manufacturer of Lifts, certifying the bidder as the authorized representative / Dealer / Vendor of the Manufacturer." Apex Infrastructure has no relationship with Otis Elevators and cannot obtain this certificate. This alone makes the tender ineligible — regardless of turnover or any other criterion.

**Second PAT-001 observation:** This tender confirms the Capability Fit pattern identified in Tender001. Road construction company evaluated against lift maintenance tender — entirely different sectors. The engine passed on turnover value alone (same failure mode as Tender001).

**Root cause split:**
- Bucket B: Regex extraction extracted 1 of ~6 requirements; missed all sector-specific and certification requirements
- Bucket C boundary: Even if extraction were complete, the engine has no sector-type matching logic to catch road-vs-lifts mismatch

## Raw Output

```
Processing: Tender002.pdf
Profile:    company-profile.json

============================================================
RECOMMENDATION: BID
Qualification Score: 100/100
Competitive Strength: 45/100
Incumbent Risk: 60/100
Execution Risk: 19/100
Value Score: 46/100
Confidence: 1.00

Reasoning:
Recommendation: BID. Qualification score: 100/100.
============================================================
```

## Extracted Requirements Detail

| # | Category | Description | Threshold | Correct? |
|---|---|---|---|---|
| 1 | turnover | Average Annual Turnover ≥ Rs. 25 Lakhs (last 3 years) | 0.25 INR_crores_annual_average | ✓ correct value |
| — | experience | Lift AMC works during last 3 years | — (no value threshold) | ✗ missed |
| — | certification | OEM certificate from Otis (authorized representative/dealer) | — | ✗ missed (hard disqualifier) |
| — | registration | Firm registration certificate | — | ✗ missed |
| — | compliance | Non-blacklisting self-declaration | — | ✗ missed |
| — | financial | PAN registration | — | ✗ missed |
| — | financial | GST registration | — | ✗ missed |
