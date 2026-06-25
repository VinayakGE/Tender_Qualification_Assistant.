# Roadmap

Seven phases from initial setup to first external pilot.

---

## Phase 1: Foundation (Current)

**Goal:** Repository structure, documentation, and data collection. Everything needed to start building.

**Deliverables:**
- Complete repository structure (all directories, schemas, prompts, docs)
- README, CONTRIBUTING, CHANGELOG
- JSON Schemas for all data contracts
- Versioned prompts for all pipeline stages
- Scoring model documented
- Decision taxonomy documented
- Recommendation engine decision tree documented
- Collect 20 historical tender PDFs (real tenders, internal use only, not committed to repo)
- Create company profile JSON for test company

**GitHub Projects columns:** Todo → In Progress → Done  
**Milestone criteria:** All docs merged to main. 20 tenders collected locally. Schema files reviewed and approved.

---

## Phase 2: Document Pipeline

**Goal:** Reliable text extraction from tender PDFs.

**Deliverables:**
- `src/parser/pdf_parser.py` — pdfplumber extraction
- `src/parser/ocr.py` — pytesseract OCR fallback
- `src/parser/cleaner.py` — text normalization
- `src/extractor/clause_extractor.py` — regex clause splitter
- `src/extractor/metadata.py` — title, authority, deadline, value extraction
- `src/extractor/requirement_extractor.py` — Claude API requirement extraction
- `scripts/parse_all.py` — batch parser CLI
- Tests: parser, extractor
- Validated on 10 of the 20 collected tenders

**Milestone criteria:** Parser extracts clean text from 90%+ of test PDFs. Requirement extractor outputs valid JSON matching schema on 80%+ of tenders without manual correction.

---

## Phase 3: Qualification Engine

**Goal:** Reliable eligibility checking against company profile.

**Deliverables:**
- `src/qualification/eligibility.py` — orchestrator
- `src/qualification/turnover.py`
- `src/qualification/experience.py`
- `src/qualification/certifications.py`
- `src/qualification/financial.py`
- Tests: all qualification checkers with boundary conditions
- Company profile schema finalized

**Milestone criteria:** Qualification results match manual expert review on 90%+ of the 20 test tenders. All four checker types covered by tests.

---

## Phase 4: Scoring Engine

**Goal:** Five-score model producing reliable numerical signals.

**Deliverables:**
- `src/scoring/qualification_score.py`
- `src/scoring/competitiveness.py`
- `src/scoring/incumbent_risk.py`
- `src/scoring/execution_risk.py`
- `src/scoring/value_score.py`
- `src/bottlenecks/classifier.py`
- `src/bottlenecks/evidence_gap.py`
- `src/bottlenecks/reasoning.py`
- Tests: scoring boundary conditions, taxonomy classifier
- `notebooks/scoring-analysis.ipynb` — calibration analysis on test tenders

**Milestone criteria:** Score distributions on 20 test tenders reviewed and calibrated. No systematic bias toward one recommendation type.

---

## Phase 5: Recommendation + Ledger

**Goal:** End-to-end pipeline producing final recommendations and logging decisions.

**Deliverables:**
- `src/recommendation/engine.py`
- `src/recommendation/confidence.py`
- `src/recommendation/explanation.py`
- `src/ledger/decisions.py`
- `src/ledger/evidence.py`
- `src/ledger/outcomes.py`
- `src/pipeline/runner.py`
- `src/pipeline/watcher.py`
- `src/pipeline/stages.py`
- `src/api/server.py` + `src/api/routes.py`
- `scripts/run_pipeline.py`
- Tests: recommendation engine (all three branches), API routes
- `decision-ledger.json` initialized (empty, committed)

**Milestone criteria:** Full pipeline runs end-to-end on all 20 test tenders. All three recommendation branches triggered at least twice in test suite. Ledger appends correctly. API `/analyze` returns valid responses.

---

## Phase 6: Internal Testing

**Goal:** Validate accuracy against human expert review on a larger dataset.

**Deliverables:**
- Run pipeline on 20-50 historical tenders
- Compare system recommendation vs. expert recommendation for each
- Identify systematic errors and tune scoring weights
- `notebooks/recommendation-analysis.ipynb` — accuracy analysis
- Outcome tracking: record actual bid results for any tenders where bid was submitted
- `scripts/export_reports.py` — decision ledger report exporter

**Milestone criteria:**
- Qualification accuracy ≥ 90% (system recommendation matches expert on 9 of 10 tenders)
- False NO BID rate ≤ 5% (system does not wrongly reject winnable tenders)
- Processing time < 60 seconds for 95% of tenders
- Decision ledger has ≥ 50 entries
- At least 5 actual bid outcomes recorded

---

## Phase 7: First External Pilot

**Goal:** One external user (a bid manager or tender consultant) uses the system on live tenders.

**Deliverables:**
- Portal integration: CPPP or GeM scraping to replace folder drop (optional — folder drop still works)
- Pilot user onboarding: company profile setup, system walkthrough
- Feedback loop: weekly check-in with pilot user, issue tracking
- Basic dashboard or report export for pilot user
- Accuracy measurement against pilot user's actual bid outcomes

**Milestone criteria:**
- Pilot user processes ≥ 10 live tenders using the system
- User NPS ≥ 7/10 on recommendation usefulness
- ≥ 3 cases where system recommendation directly influenced go/no-go decision
- At least 1 actual bid outcome recorded from pilot

---

## GitHub Projects Board Structure

| Column | Description |
|---|---|
| Backlog | All known tasks, not yet prioritized |
| Ready | Prioritized and scoped, ready to start |
| In Progress | Actively being worked on |
| In Review | PR open, awaiting review |
| Done | Merged to main |

Labels: `phase-1` through `phase-7`, `bug`, `prompt`, `schema`, `docs`, `test`, `enhancement`
