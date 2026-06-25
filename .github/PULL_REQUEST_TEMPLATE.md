## Summary

<!-- What does this PR do? 2-3 sentences max. -->


## Changes

<!-- Bullet list of what was changed and why. -->

- 
- 

## Testing

<!-- How was this tested? Check all that apply. -->

- [ ] `pytest tests/` passes locally
- [ ] `ruff check src/ tests/ scripts/` passes with no errors
- [ ] Tested manually on sample tender(s) with `scripts/run_pipeline.py`
- [ ] API endpoint tested with curl or httpx

## Schema / Prompt Changes

<!-- If you changed any files in schemas/ or prompts/, fill this out. -->

**Schema changes:** <!-- None / List changed schemas and what fields were added/removed/changed -->

**Prompt changes:** <!-- None / Describe what changed in the prompt and why. Include before/after examples if the output format changed. -->

**Tested prompt changes on:**
- [ ] At least 3 sample tenders
- [ ] Output validated against schema

## Pipeline Stage(s) Affected

<!-- Which pipeline stage(s) does this touch? -->

- [ ] Parser
- [ ] Extractor
- [ ] Qualification
- [ ] Scoring
- [ ] Bottleneck Classifier
- [ ] Recommendation Engine
- [ ] Ledger
- [ ] API
- [ ] Watcher / Pipeline Runner
- [ ] Documentation only

## Checklist

- [ ] CHANGELOG.md updated under `[Unreleased]`
- [ ] New functions/classes have docstrings
- [ ] Type hints added to all new public functions
- [ ] No real tender documents committed (sample data only)
- [ ] No API keys or credentials in any committed file
- [ ] PR title follows commit style: `type(scope): description`
