# Tender 01

## Source

| Field | Value |
|---|---|
| Portal | |
| Tender ID / Reference | |
| Issuing Authority | |
| Work Description | |
| Estimated Value | |
| Download URL | |
| Downloaded On | |

## Pipeline Run

```
python scripts/run_pipeline.py \
  --pdf data/incoming/<filename>.pdf \
  --profile data/company-profiles/<company>.json
```

| Metric | Result |
|---|---|
| Parser succeeded | Yes / No |
| Characters extracted | |
| Extraction method | pdfplumber / stream / ocr |
| Requirements found | |
| Manual edits needed | 0 |
| Recommendation generated | Yes / No |
| Recommendation | BID / REVIEW / NO_BID / — |
| Expected Recommendation | Unknown |
| Qualification score | /100 |
| Incumbent risk | /100 |
| Pipeline duration | seconds |

## Failure Bucket

<!-- If the pipeline failed or the recommendation was wrong, classify the root cause:
     A — Engineering (parser crash, OCR failure, pipeline error)
     B — Extraction (missed clause, wrong threshold, wrong category)
     C — Decision (correct extraction, wrong recommendation)
     Leave blank if pipeline succeeded and recommendation was correct. -->

Bucket: —

## Observations

<!-- What happened. One paragraph. No fixes, no proposals — just what you saw. -->

## Raw output

```
(paste the ==== block here)
```
