# Tender Qualification Assistant

Decision intelligence for government procurement. Drop a tender PDF, get a qualification verdict in under 60 seconds.

## What It Does

The system reads a tender document, checks it against a company profile, and returns a structured recommendation — **BID**, **REVIEW**, or **NO BID** — before any human time is spent.

```
incoming PDF  →  parse  →  extract requirements  →  qualify  →  score  →  recommend  →  ledger
```

## Repository Layout

```
.
├── data/
│   ├── incoming/          # Drop tender PDFs here to trigger pipeline
│   ├── raw-tenders/       # PDFs after ingestion
│   ├── parsed-tenders/    # Extracted text + structured JSON
│   ├── company-profiles/  # Company profile JSONs
│   ├── historical-decisions/
│   ├── outcomes/          # Recommendation outputs
│   └── sample-data/       # Synthetic test data
├── docs/                  # Architecture, scoring model, roadmap
├── prompts/               # Versioned LLM prompts
├── schemas/               # JSON Schemas for all data contracts
├── src/
│   ├── api/               # FastAPI server + routes
│   ├── bottlenecks/       # Gap detection + reasoning
│   ├── extractor/         # PDF → structured requirements
│   ├── ledger/            # Decision logging + outcome tracking
│   ├── parser/            # PDF text extraction
│   ├── pipeline/          # Orchestration + folder watcher
│   ├── qualification/     # Eligibility checks
│   ├── recommendation/    # Decision engine
│   ├── scoring/           # Five-score model
│   └── utils/             # Config, logging, helpers
├── tests/                 # Pytest suite
├── scripts/               # CLI utilities
├── notebooks/             # Exploratory analysis
└── .github/workflows/     # CI + automated pipeline stages
```

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Set ANTHROPIC_API_KEY in .env
```

### 3. Run on a single tender

```bash
python scripts/run_pipeline.py \
  --pdf data/incoming/my_tender.pdf \
  --profile data/company-profiles/my_company.json
```

### 4. Drop-and-go automation

Start the folder watcher:

```bash
python -m src.pipeline.watcher
```

Then drop any PDF into `data/incoming/`. The watcher looks for a matching `<stem>_profile.json` in `data/company-profiles/` and runs the full pipeline automatically.

### 5. Run the API server

```bash
uvicorn src.api.server:app --reload
# POST /analyze with form: tender_pdf + company_profile_json
```

## Decision Framework

| Condition | Recommendation |
|---|---|
| Any mandatory requirement unmet | NO BID |
| Qualification score < 60 | NO BID |
| Score 60-79, no critical evidence gaps | REVIEW |
| Score 80+, critical evidence gaps present | REVIEW |
| Score 80+, evidence complete, incumbent risk < 70 | BID |
| Score 80+, evidence complete, incumbent risk ≥ 70 | REVIEW |

## Output Format

```json
{
  "recommendation": "REVIEW",
  "qualification_score": 84,
  "competitive_strength": 71,
  "incumbent_risk": 55,
  "execution_risk": 38,
  "value_score": 67,
  "primary_bottleneck": "Missing Experience Evidence",
  "evidence_gaps": ["ISO 27001 certificate", "Similar project completion certificate > 5Cr"],
  "confidence": 0.81,
  "reasoning": "Company meets turnover and certification thresholds but lacks documented evidence of comparable project completion."
}
```

## Scores at a Glance

| Score | Range | Meaning |
|---|---|---|
| Qualification Fit | 0-100 | % of mandatory requirements met (80+ = PASS) |
| Competitive Strength | 0-100 | Company's relative strength in this tender category |
| Incumbent Risk | 0-100 | Likelihood of existing vendor retention (70+ = high risk) |
| Execution Risk | 0-100 | Delivery risk based on scope, timeline, capacity |
| Value Score | 0-100 | Composite: contract value + strategic fit + win probability |

## Documentation

- [Vision & Mission](docs/vision.md)
- [Architecture](docs/architecture.md)
- [Scoring Model](docs/scoring-model.md)
- [Recommendation Engine Logic](docs/recommendation-engine.md)
- [Decision Taxonomy](docs/decision-taxonomy.md)
- [Roadmap](docs/roadmap.md)
- [MVP Scope](docs/mvp-scope.md)
- [Workflow](docs/workflow.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

See [LICENSE](LICENSE).
