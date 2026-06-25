# Architecture

## System Overview

The Tender Qualification Assistant is an event-driven pipeline. A PDF enters at one end; a structured recommendation exits at the other. Each stage in the pipeline has a well-defined input and output, separated by JSON data contracts defined in `schemas/`.

```
data/incoming/ (PDF drop)
        │
        │  [Folder Watcher / GitHub Action]
        │
        ▼
┌─────────────────────────────────┐
│         Parser Engine            │
│  pdfplumber → text extraction    │
│  pytesseract → OCR fallback      │
│  TextCleaner → normalization     │
└──────────────┬──────────────────┘
               │  clean text (str)
               ▼
┌─────────────────────────────────┐
│      Requirement Extractor       │
│  ClauseExtractor → split text    │
│  MetadataExtractor → title etc   │
│  RequirementExtractor (Claude)   │
│  → list[Requirement] JSON        │
└──────────────┬──────────────────┘
               │  requirements[] + metadata
               ▼
┌─────────────────────────────────┐
│       Qualification Engine       │
│  TurnoverChecker                 │
│  ExperienceChecker               │
│  CertificationChecker            │
│  FinancialChecker                │
│  → EligibilityResult             │
└──────────────┬──────────────────┘
               │  eligibility_result
               ▼
┌─────────────────────────────────┐
│         Scoring Engine           │
│  QualificationScorer  → 0-100   │
│  CompetitivenessScorer → 0-100  │
│  IncumbentRiskScorer  → 0-100   │
│  ExecutionRiskScorer  → 0-100   │
│  ValueScorer          → 0-100   │
└──────────────┬──────────────────┘
               │  five scores
               ▼
┌─────────────────────────────────┐
│      Bottleneck Classifier       │
│  BottleneckClassifier            │
│  EvidenceGapDetector             │
│  ReasoningBuilder                │
└──────────────┬──────────────────┘
               │  bottleneck + evidence_gaps + reasoning
               ▼
┌─────────────────────────────────┐
│      Recommendation Engine       │
│  Decision tree (rule-based)      │
│  ConfidenceEstimator             │
│  ExplanationGenerator (Claude)   │
│  → Recommendation JSON           │
└──────────────┬──────────────────┘
               │  recommendation
               ▼
┌─────────────────────────────────┐
│         Decision Ledger          │
│  decision-ledger.json (append)   │
│  → PostgreSQL (Phase 5+)         │
└──────────────┬──────────────────┘
               │
               ▼
        data/outcomes/
   <tender_id>_recommendation.json

               │
               ▼
┌─────────────────────────────────┐
│       Dashboard / API            │
│  FastAPI  → POST /analyze        │
│           → GET /ledger          │
│           → POST /outcomes/{id}  │
└─────────────────────────────────┘
```

---

## Component Breakdown

### Trigger Layer

Two trigger mechanisms are supported:

1. **Folder Watcher** (`src/pipeline/watcher.py`): Uses the `watchdog` library to monitor `data/incoming/`. On a `FileCreatedEvent` for a `.pdf` file, looks for a matching company profile and invokes `PipelineRunner.run()`.

2. **GitHub Actions** (`.github/workflows/`): A set of five workflow files that chain together as data flows through the pipeline. Suitable for batch processing and CI automation.

### Parser Engine

- `PDFParser.extract_text()`: Iterates pages with pdfplumber. If average characters per page < 100 (indicating a scanned document), falls back to OCR.
- `OCRExtractor.extract()`: Renders PDF pages as images using PIL, runs pytesseract on each page, concatenates output.
- `TextCleaner.clean()`: Strips headers/footers (detected by page-boundary repetition), normalizes Unicode, collapses whitespace.

**Input:** PDF file path  
**Output:** Clean UTF-8 text string

### Requirement Extractor

- `ClauseExtractor.extract_clauses()`: Splits text on numbered clause patterns common in Indian government tenders (e.g., `3.1`, `Section 4.2`, `Clause 5`).
- `MetadataExtractor.extract()`: Uses regex to find tender ID, title, authority name, dates, and contract value.
- `RequirementExtractor.extract()`: Loads `prompts/requirement-extractor.md`, calls Claude API with the tender text, parses JSON response into `list[Requirement]`.

**Input:** Clean text string  
**Output:** `list[Requirement]` + tender metadata

### Qualification Engine

Each checker receives the full `list[Requirement]` and the company profile, filters to the relevant requirement category, and returns per-requirement pass/fail/gap results.

- `TurnoverChecker`: Compares `company.annual_turnover_inr_crores` (3-year average) against turnover requirements.
- `ExperienceChecker`: Checks if any completed project matches the value, sector, and time window requirements.
- `CertificationChecker`: Checks if all required certifications are in `company.certifications`.
- `FinancialChecker`: Compares net worth and working capital against thresholds.

**Input:** `list[Requirement]`, company profile dict  
**Output:** `EligibilityResult` with `overall_pass: bool` and per-requirement results

### Scoring Engine

Five independent scorers, each taking the eligibility result plus raw tender and company data. All run after qualification; scores are not computed if a mandatory requirement has already failed (performance optimization).

**Input:** `EligibilityResult`, tender metadata, company profile  
**Output:** Five integer scores 0-100

### Bottleneck Classifier

- `BottleneckClassifier.classify()`: Maps failure types to taxonomy labels from `docs/decision-taxonomy.md`.
- `EvidenceGapDetector.detect()`: For each passing requirement, checks if the company profile has supporting evidence (not just meeting the threshold numerically, but having a document to prove it).
- `ReasoningBuilder.build()`: Constructs a structured reasoning string for the primary bottleneck.

**Input:** Eligibility result, scores  
**Output:** `primary_bottleneck: str`, `evidence_gaps: list[str]`, `reasoning_text: str`

### Recommendation Engine

- `RecommendationEngine.recommend()`: Applies the decision tree from `docs/recommendation-engine.md`. Returns a `Recommendation` object with the verdict and scores.
- `ConfidenceEstimator.estimate()`: Computes confidence from data completeness, score margins, and requirement coverage.
- `ExplanationGenerator.generate()`: Calls Claude with `prompts/recommendation.md` to write the explanation paragraph.

**Input:** All scores, bottleneck, evidence gaps  
**Output:** `Recommendation` (Pydantic model)

### Decision Ledger

- `DecisionLedger.append()`: Thread-safe append to `decision-ledger.json` using `fcntl` file locking. JSON file grows incrementally; PostgreSQL migration planned for Phase 5+.
- `OutcomeTracker.record()`: Writes actual bid outcome against a recommendation ID.

**Input:** `Recommendation` object  
**Output:** Updated `decision-ledger.json`

### API Layer

FastAPI application with three route groups:

- `POST /analyze`: Accepts multipart form with `tender_pdf` (file) and `company_profile_json` (JSON string or file). Runs full pipeline. Returns recommendation JSON.
- `GET /ledger`: Paginated list of all decisions.
- `GET /ledger/{id}`: Single decision by ID.
- `POST /outcomes/{id}`: Record actual bid outcome.

---

## Data Contracts

All inter-stage data is defined by JSON Schemas in `schemas/`:

| Schema | File | Used between |
|---|---|---|
| Requirement | `schemas/requirement.schema.json` | Extractor → Qualification |
| Company Profile | `schemas/company.schema.json` | User input → All stages |
| Tender | `schemas/tender.schema.json` | Extractor → Qualification |
| Evidence | `schemas/evidence.schema.json` | Qualification → Bottleneck |
| Recommendation | `schemas/recommendation.schema.json` | Recommendation → Ledger |
| Outcome | `schemas/outcome.schema.json` | Outcome Tracker → Ledger |

---

## Technology Choices

| Technology | Choice | Rationale |
|---|---|---|
| LLM | Claude (anthropic SDK) | Best-in-class for structured data extraction from documents; JSON mode is reliable |
| PDF extraction | pdfplumber | Accurate text extraction with layout awareness; handles tables better than pypdf |
| OCR | pytesseract | Standard, reliable; sufficient for government tender PDFs |
| Data validation | Pydantic v2 | Fast, type-safe, excellent JSON Schema integration |
| Web API | FastAPI | Async-native, auto-generates OpenAPI docs, Pydantic integration |
| Logging | structlog | Structured JSON logs; plays well with observability tools |
| File watching | watchdog | Cross-platform, well-maintained, simple API |
| Testing | pytest | Standard; async support via pytest-asyncio |
| Linting | ruff | Fast, replaces flake8+isort+black |

---

## Future Architecture (Phase 5+)

- Replace `decision-ledger.json` with PostgreSQL (asyncpg + SQLAlchemy)
- Add Redis for pipeline job queuing when running as a service
- Add portal scrapers as alternative trigger sources (CPPP, GeM, state portals)
- Add a React dashboard consuming the FastAPI
- Add background job processing via Celery or equivalent
