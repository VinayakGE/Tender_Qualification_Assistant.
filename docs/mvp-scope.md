# MVP Scope

## The One Question the MVP Answers

> **Should we bid this tender?**

Everything else is out of scope until the answer to that question is reliable, fast, and explainable.

---

## Inputs

| Input | Format | Notes |
|---|---|---|
| Tender document | PDF | Any government tender PDF. Text-layer preferred; OCR fallback for scanned documents. |
| Company profile | JSON | Structured profile matching `schemas/company.schema.json`. Created once, reused for all tenders. |

No portal credentials required. No live internet access required. Both inputs can be provided as local files.

---

## Output

A single recommendation JSON matching `schemas/recommendation.schema.json`:

```json
{
  "recommendation_id": "rec_20240615_apex_t001",
  "tender_id": "T001",
  "company_id": "SAMPLE-001",
  "recommendation": "REVIEW",
  "qualification_score": 84,
  "competitive_strength": 71,
  "incumbent_risk": 55,
  "execution_risk": 38,
  "value_score": 67,
  "primary_bottleneck": "Missing Experience Evidence",
  "evidence_gaps": [
    "ISO 27001 certificate not in company profile",
    "Similar project >5Cr completion certificate not documented"
  ],
  "confidence": 0.81,
  "reasoning": "Company meets turnover and core certification thresholds. Qualification score of 84 passes the 80+ threshold. However, two evidence gaps prevent a clean BID recommendation: the tender requires ISO 27001 and documented experience on projects above 5 Cr — neither is present in the company profile. Recommend REVIEW to confirm whether evidence exists and can be produced.",
  "created_at": "2024-06-15T10:23:44Z"
}
```

---

## What Is In Scope

- PDF ingestion via local file or folder drop into `data/incoming/`
- Text extraction from digital PDFs (pdfplumber)
- OCR fallback for scanned PDFs (pytesseract)
- Structured requirement extraction via Claude API
- Rule-based eligibility checking against company profile
- Five-score model: qualification fit, competitive strength, incumbent risk, execution risk, value score
- Decision tree producing BID / REVIEW / NO BID
- Primary bottleneck classification
- Evidence gap detection
- Natural language reasoning paragraph
- Append to `decision-ledger.json`
- REST API (`POST /analyze`)
- CLI script (`scripts/run_pipeline.py`)
- Folder watcher for automated pipeline (`src/pipeline/watcher.py`)

---

## What Is Out of Scope for MVP

| Feature | When |
|---|---|
| Portal scraping (CPPP, GeM, state portals) | Phase 7 |
| Dashboard UI | After Phase 5 |
| Multi-company comparison (which company is best fit for this tender) | Post-pilot |
| Outcome tracking and accuracy measurement | Phase 6 |
| ML-based scoring (replacing rule-based heuristics) | Post-pilot, after ledger has sufficient data |
| Automated bid writing or proposal assistance | Never — out of product scope |
| Real-time alerts / notifications | After Phase 6 |
| Multi-language tender support (regional languages) | Post-pilot |
| PostgreSQL migration from JSON ledger | Phase 5+ |

---

## Definition of Done for MVP

The MVP is done when:

1. A single PDF + profile JSON can be processed end-to-end in under 60 seconds
2. The output recommendation JSON is valid against `schemas/recommendation.schema.json`
3. All three decision branches (BID / REVIEW / NO BID) are reachable and produce correct outputs on test cases
4. The decision is appended to `decision-ledger.json`
5. Tests pass for parser, extractor, qualification, scoring, and recommendation stages
6. The folder watcher triggers the pipeline automatically on PDF drop
7. The REST API `/analyze` endpoint returns a valid response
