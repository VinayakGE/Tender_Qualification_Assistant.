# RA-1 Sprint Baseline

This file is the authoritative baseline reference for the RA-1 Reality Acquisition sprint.
Git tags were not pushed (proxy restriction); use the commit hash below as the baseline anchor.

| Field              | Value                                      |
|--------------------|-------------------------------------------|
| Sprint             | RA-1                                       |
| Baseline Commit    | 9a38200                                    |
| Branch             | claude/loving-noether-k7d2fr               |
| Date Locked        | 2026-06-25                                 |
| Extractor Version  | v0.1.0                                     |
| Prompt Version     | 1.1.0                                      |
| Schema Version     | 1.1                                        |
| Test Suite         | 58/58 passing                              |
| Extraction Mode    | LLM (Claude API) / Regex fallback offline  |

## What is frozen

All Type 2 behavior is frozen at this commit:

- Qualification rules (`src/qualification/eligibility.py`)
- Scoring weights (`src/scoring/`)
- Recommendation logic (`src/recommendation/`)
- Requirement extraction prompt (`prompts/requirement-extractor.md`)
- Regex fallback patterns (`src/extractor/requirement_extractor.py`)

## What is allowed during RA-1

Type 1 observation infrastructure only:

- Logging improvements
- Evidence form updates
- Accuracy report entries
- Schema documentation (no behavior change)

## Evidence gate

No Type 2 change may be committed until `RA-1-Summary.md` is complete and
the change satisfies the evidence-linked commit format in `CONTRIBUTING.md`.
