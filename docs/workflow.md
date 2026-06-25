# Workflow

## End-to-End Pipeline

```
Tender PDF
    │
    ▼
1. Document Parsing
    │  pdfplumber extracts text layer
    │  OCR fallback (pytesseract) if text is sparse
    │  TextCleaner normalizes whitespace, removes headers/footers
    │
    ▼
2. Requirement Extraction
    │  ClauseExtractor splits document into numbered sections
    │  MetadataExtractor pulls title, authority, deadline, contract value
    │  RequirementExtractor (Claude API) identifies each eligibility requirement:
    │    - Turnover thresholds (annual, average)
    │    - Experience requirements (project value, type, sector, duration)
    │    - Certifications (ISO standards, sector-specific certs)
    │    - Financial ratios (net worth, working capital, solvency)
    │    - Technical specifications
    │    - Flags each requirement as mandatory or optional
    │
    ▼
3. Qualification Check
    │  EligibilityChecker runs each requirement against company profile:
    │    - TurnoverChecker: average annual turnover ≥ threshold?
    │    - ExperienceChecker: completed project of required value/type?
    │    - CertificationChecker: company holds required cert?
    │    - FinancialChecker: net worth / working capital ≥ threshold?
    │  Result: per-requirement pass/fail/gap + overall pass/fail
    │
    ▼
4. Scoring
    │  Five scores computed in parallel:
    │    - QualificationScorer: 0-100, mandatory reqs weighted 2x
    │    - CompetitivenessScorer: company's relative competitive position
    │    - IncumbentRiskScorer: heuristic from tender language signals
    │    - ExecutionRiskScorer: scope/timeline/capacity risk
    │    - ValueScorer: contract value + strategic fit + win probability
    │
    ▼
5. Bottleneck Classification
    │  BottleneckClassifier maps raw failures to taxonomy labels:
    │    e.g. "annual_turnover < threshold" → "Turnover Requirement Gap"
    │  EvidenceGapDetector identifies which requirements have no
    │    supporting evidence in the company profile
    │  ReasoningBuilder assembles human-readable reasoning text
    │
    ▼
6. Recommendation
    │  RecommendationEngine applies decision tree:
    │    - Any mandatory requirement unmet → NO BID
    │    - qualification_score < 60 → NO BID
    │    - score 60-79, no critical gaps → REVIEW
    │    - score 80+, critical gaps → REVIEW
    │    - score 80+, no gaps, incumbent_risk < 70 → BID
    │    - score 80+, no gaps, incumbent_risk ≥ 70 → REVIEW
    │  ConfidenceEstimator produces 0-1 confidence score
    │  ExplanationGenerator (Claude API) writes reasoning paragraph
    │
    ▼
7. Decision Ledger
       DecisionLedger appends recommendation to decision-ledger.json
       Recommendation JSON written to data/outcomes/
```

---

## Folder-Triggered Automation

The simplest way to run the pipeline is to drop a PDF into `data/incoming/`.

### Setup

Start the folder watcher:

```bash
python -m src.pipeline.watcher
```

Or, if using the GitHub Actions workflow, the watcher runs as part of the CI pipeline.

### Naming Convention

For the watcher to match a tender to a company profile automatically, use this naming convention:

- Tender PDF: `data/incoming/my_tender_001.pdf`
- Company profile: `data/company-profiles/my_tender_001_profile.json`

The watcher strips the `_profile` suffix and matches on the stem. If no profile is found for a given PDF, the watcher logs a warning and uses the default profile from `data/company-profiles/default_profile.json` if it exists.

### What Happens

1. PDF appears in `data/incoming/`
2. Watcher detects the new file (watchdog FileCreatedEvent)
3. Watcher looks for matching `<stem>_profile.json` in `data/company-profiles/`
4. `PipelineRunner.run(pdf_path, profile_path)` is called
5. Result JSON is written to `data/outcomes/<stem>_recommendation.json`
6. PDF is moved to `data/raw-tenders/`
7. Decision is appended to `decision-ledger.json`

### Output Location

```
data/
├── incoming/          ← drop PDF here
├── raw-tenders/       ← PDF moved here after processing
├── parsed-tenders/    ← extracted text saved here
├── outcomes/          ← recommendation JSON saved here
└── company-profiles/  ← company profile JSONs
```

---

## Manual Pipeline via CLI

Run a single tender manually:

```bash
python scripts/run_pipeline.py \
  --pdf path/to/tender.pdf \
  --profile path/to/company_profile.json
```

Output is printed to stdout and saved to `data/outcomes/`.

---

## API-Triggered Pipeline

Send a tender via the REST API:

```bash
curl -X POST http://localhost:8000/analyze \
  -F "tender_pdf=@tender.pdf" \
  -F "company_profile_json=@company_profile.json"
```

Response:

```json
{
  "recommendation": "BID",
  "qualification_score": 88,
  "primary_bottleneck": null,
  "confidence": 0.91
}
```

---

## GitHub Actions Pipeline (Automated)

When the repository is used as the pipeline backend, the GitHub Actions workflows trigger each stage automatically:

| Workflow | Trigger | Action |
|---|---|---|
| `01-ingest.yml` | Daily 6am / manual | Scans for new PDFs, commits to `data/raw-tenders/` |
| `02-extract.yml` | Push to `data/raw-tenders/**` | Runs requirement extraction, commits to `data/parsed-tenders/` |
| `03-qualify.yml` | Push to `data/parsed-tenders/**` | Runs qualification, appends scores |
| `04-recommend.yml` | Push to `data/parsed-tenders/**` | Runs full pipeline, commits recommendation |
| `05-ledger.yml` | Push to `decision-ledger.json` | Generates summary report in `data/outcomes/` |

See `.github/workflows/` for full configuration.
