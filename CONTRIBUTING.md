# Contributing to Tender Qualification Assistant

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, production-ready code only |
| `feature/*` | New features (e.g., `feature/scoring-engine`) |
| `fix/*` | Bug fixes (e.g., `fix/turnover-threshold-edge-case`) |
| `docs/*` | Documentation-only changes |
| `chore/*` | Tooling, deps, CI (e.g., `chore/update-ruff-config`) |

Never push directly to `main`. All changes go through a PR.

## Development Workflow

1. **Branch from main**
   ```bash
   git checkout main && git pull
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**
   - Write code in `src/`
   - Add or update tests in `tests/`
   - Update prompts in `prompts/` if LLM behavior changes
   - Update schemas in `schemas/` if data contracts change

3. **Run tests locally**
   ```bash
   pytest tests/ -v
   ```

4. **Run linter**
   ```bash
   ruff check src/ tests/ scripts/
   ruff format src/ tests/ scripts/
   ```

5. **Open a PR**
   - Fill in the PR template completely
   - Reference any related issues
   - Mark schema and prompt changes explicitly — these are versioned artifacts

## Commit Message Style

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

[optional body]
```

| Type | Use for |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code restructure without behavior change |
| `test` | Adding or fixing tests |
| `chore` | Tooling, deps, CI changes |
| `prompt` | Changes to LLM prompts in `prompts/` |
| `schema` | Changes to JSON schemas in `schemas/` |

**Examples:**

```
feat(scoring): add incumbent risk heuristic scorer
fix(parser): handle PDFs with no extractable text layer
prompt(extractor): tighten turnover extraction instruction
schema(recommendation): add evidence_gaps array field
test(qualification): add boundary test for 60-score threshold
```

Keep the subject line under 72 characters. Use the body for _why_, not _what_.

## Evidence-Linked Engineering (Post-RA-1 Rule)

Every code change that modifies pipeline behavior must reference the observed evidence that justified it. Use this structure in the commit body:

```
Finding:
<what was observed across multiple tenders>

Evidence:
<N/10 tenders affected, Tender IDs>

Impact:
High / Medium / Low — <what the failure actually costs>

Change:
<what was changed and why this addresses the root cause>
```

**Example:**

```
fix(extractor): scan Annexure B for JV eligibility clauses

Finding:
JV eligibility clauses consistently appear in Annexure B, not the
main tender body. The extractor missed these in all cases.

Evidence:
3/10 tenders (Tender003, Tender007, Tender009). All three were road
construction tenders issued by state highway authorities.

Impact:
High — misclassified these tenders as eligible when JV was mandatory.
Would have triggered disqualification post-submission.

Change:
Extractor now checks for Annexure B section header and includes its
text in the eligibility extraction pass.
```

A commit that says "improved parser" with no evidence reference will be rejected in PR review. Opinion without observation has no weight here.

## Prompts as Versioned Artifacts

Prompts in `prompts/` are first-class code artifacts, not just configuration:

- **Every prompt change gets its own commit** with type `prompt`
- Include the reason for the change in the commit body (e.g., "was extracting optional reqs as mandatory in ambiguous clauses")
- If a prompt change affects output schema, update the schema and tests in the same PR
- Do not inline prompts into Python source — always load from the `prompts/` directory

When testing a prompt change:
1. Run the affected pipeline stage on at least 3 sample tenders
2. Compare structured outputs before and after
3. Document examples in the PR description

## Data Policy

**No real tender documents in the repository — ever.**

- Use only synthetic or anonymized samples in `data/sample-data/`
- Real tenders processed during development stay local and are never committed
- Company profiles must use fictional company names and scrambled financials
- The `data/` directories (except `sample-data/`) are gitignored for this reason

If you need a realistic test case, create a synthetic tender that mimics the structure without using real procurement details. See `data/sample-data/sample_company_profile.json` for the expected format.

## Adding a New Pipeline Stage

If you add a new processing stage:

1. Add the stage class in the appropriate `src/` subdirectory
2. Register it in `src/pipeline/runner.py`
3. Add a `PipelineStage` entry in `src/pipeline/stages.py`
4. Add tests in the corresponding `tests/` subdirectory
5. Update `docs/architecture.md` with the new stage
6. Update `CHANGELOG.md` under `[Unreleased]`

## Schema Changes

Schema files in `schemas/` define data contracts between pipeline stages. Before changing a schema:

1. Check which stages produce and consume that schema
2. Update all affected Pydantic models in `src/`
3. Update tests
4. Bump the schema `$schema` version comment
5. Note the change in `CHANGELOG.md`

Breaking schema changes (removing fields, changing types) require a major version bump.

## Code Style

- Python 3.11+
- Type hints on all public functions and methods
- Pydantic v2 for all data models
- structlog for all logging (no `print()` in production code)
- Line length: 100 characters (enforced by ruff)
- Imports: sorted by ruff (isort-compatible)

## Questions

Open an issue with the `question` label or start a discussion in GitHub Discussions.
