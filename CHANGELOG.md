# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Repository Structure
- Complete repository scaffolding with all directories and placeholder files
- `.gitkeep` files for `data/incoming/`, `data/raw-tenders/`, `data/parsed-tenders/`, `data/company-profiles/`, `data/historical-decisions/`, `data/outcomes/`, `data/sample-data/`
- `.gitkeep` files for `web/dashboard/`, `web/components/`, `web/pages/`, `web/assets/`

#### Documentation
- `docs/vision.md` — Problem statement, mission, product vision, and success metrics
- `docs/product-principles.md` — Five core product principles
- `docs/mvp-scope.md` — MVP scope definition (in vs out of scope)
- `docs/customer-persona.md` — Four primary user personas with goals and pain points
- `docs/workflow.md` — End-to-end workflow narrative with folder-triggered automation
- `docs/scoring-model.md` — Full scoring model with formulas, ranges, and thresholds
- `docs/decision-taxonomy.md` — Mapping of internal reasoning to product language
- `docs/recommendation-engine.md` — Complete decision tree with all conditions and thresholds
- `docs/roadmap.md` — Seven-phase roadmap from setup to pilot
- `docs/architecture.md` — System architecture with ASCII diagram and data contracts

#### Schemas
- `schemas/tender.schema.json` — JSON Schema for parsed tender documents
- `schemas/requirement.schema.json` — JSON Schema for individual requirements
- `schemas/company.schema.json` — JSON Schema for company profiles
- `schemas/recommendation.schema.json` — JSON Schema for output recommendations
- `schemas/evidence.schema.json` — JSON Schema for evidence items
- `schemas/outcome.schema.json` — JSON Schema for bid outcomes

#### Prompts (versioned LLM artifacts)
- `prompts/parser.md` — Prompt for cleaning raw PDF-extracted text
- `prompts/requirement-extractor.md` — Prompt for structured requirement extraction
- `prompts/qualification.md` — Prompt for eligibility checking
- `prompts/recommendation.md` — Prompt for final recommendation generation
- `prompts/validation.md` — Prompt for JSON schema validation

#### Source Code
- `src/utils/config.py` — Pydantic BaseSettings configuration
- `src/utils/logger.py` — Structured logging with structlog
- `src/utils/helpers.py` — Utility functions (slugify, load_json, save_json, etc.)
- `src/parser/pdf_parser.py` — PDF text extraction with pdfplumber and OCR fallback
- `src/parser/ocr.py` — OCR extraction using pytesseract
- `src/parser/cleaner.py` — Text normalization and cleaning
- `src/extractor/clause_extractor.py` — Regex-based clause splitting for Indian government tenders
- `src/extractor/requirement_extractor.py` — LLM-powered requirement extraction via Claude API
- `src/extractor/metadata.py` — Tender metadata extraction (title, authority, dates, value)
- `src/qualification/eligibility.py` — Overall eligibility checker orchestrating all sub-checks
- `src/qualification/turnover.py` — Annual turnover threshold checker
- `src/qualification/experience.py` — Project experience checker
- `src/qualification/certifications.py` — Certification checker
- `src/qualification/financial.py` — Financial threshold checker (net worth, working capital)
- `src/scoring/qualification_score.py` — Qualification fit scorer (mandatory 2x weight)
- `src/scoring/competitiveness.py` — Competitive position estimator
- `src/scoring/incumbent_risk.py` — Incumbent risk heuristic scorer
- `src/scoring/execution_risk.py` — Execution risk scorer
- `src/scoring/value_score.py` — Composite value scorer
- `src/bottlenecks/classifier.py` — Bottleneck taxonomy classifier
- `src/bottlenecks/evidence_gap.py` — Evidence gap detector
- `src/bottlenecks/reasoning.py` — Human-readable reasoning builder
- `src/recommendation/engine.py` — Core decision engine implementing the full decision tree
- `src/recommendation/confidence.py` — Confidence score estimator
- `src/recommendation/explanation.py` — LLM-powered natural language explanation generator
- `src/ledger/decisions.py` — Thread-safe decision ledger with file locking
- `src/ledger/evidence.py` — Evidence store
- `src/ledger/outcomes.py` — Bid outcome tracker
- `src/api/server.py` — FastAPI application factory
- `src/api/routes.py` — API routes: /analyze, /ledger, /outcomes
- `src/pipeline/runner.py` — Full pipeline orchestrator
- `src/pipeline/watcher.py` — Folder watcher for automated pipeline triggering
- `src/pipeline/stages.py` — Pipeline stage observability dataclass

#### Tests
- `tests/conftest.py` — Shared pytest fixtures
- `tests/parser/test_pdf_parser.py` — Parser unit tests
- `tests/extractor/test_requirement_extractor.py` — Extractor unit tests with mocked Claude API
- `tests/qualification/test_eligibility.py` — Eligibility checker tests
- `tests/scoring/test_qualification_score.py` — Scoring tests with boundary conditions
- `tests/recommendation/test_engine.py` — Decision engine tests for all three branches
- `tests/api/test_routes.py` — API endpoint tests with mocked pipeline

#### Scripts
- `scripts/ingest_tenders.py` — Batch PDF ingestion CLI
- `scripts/parse_all.py` — Batch parsing CLI
- `scripts/score_all.py` — Batch scoring CLI
- `scripts/export_reports.py` — Decision ledger Markdown report exporter
- `scripts/run_pipeline.py` — Single-tender end-to-end pipeline CLI

#### Notebooks
- `notebooks/parser-experiments.ipynb` — PDF parser experiments
- `notebooks/scoring-analysis.ipynb` — Scoring model analysis
- `notebooks/recommendation-analysis.ipynb` — Recommendation engine analysis

#### CI/CD
- `.github/workflows/tests.yml` — Pytest on push and PR to main
- `.github/workflows/lint.yml` — Ruff linting on push and PR to main
- `.github/workflows/01-ingest.yml` — Daily tender ingestion (stub, Phase 7 portal integration)
- `.github/workflows/02-extract.yml` — Requirement extraction triggered on new raw tenders
- `.github/workflows/03-qualify.yml` — Qualification triggered on new parsed tenders
- `.github/workflows/04-recommend.yml` — Recommendation triggered on parsed tenders
- `.github/workflows/05-ledger.yml` — Ledger update triggered on decision-ledger.json push

#### Sample Data
- `data/sample-data/sample_company_profile.json` — Synthetic company profile for testing

#### Project Config
- `requirements.txt` — Production + dev dependencies
- `pyproject.toml` — Project metadata, ruff config, pytest config
- `.github/PULL_REQUEST_TEMPLATE.md` — PR template with pipeline stage checklist
- `.github/ISSUE_TEMPLATE/bug_report.md` — Bug report template
- `.github/ISSUE_TEMPLATE/feature_request.md` — Feature request template
