---
name: Bug Report
about: Report a bug in the Tender Qualification Assistant
title: "[BUG] "
labels: bug
assignees: ''
---

## Bug Description

<!-- A clear, concise description of what the bug is. -->


## Pipeline Stage

<!-- Which stage of the pipeline is affected? -->

- [ ] Parser (PDF text extraction)
- [ ] Extractor (requirement extraction)
- [ ] Qualification (eligibility check)
- [ ] Scoring (score computation)
- [ ] Bottleneck Classifier
- [ ] Recommendation Engine
- [ ] Ledger
- [ ] API
- [ ] Folder Watcher
- [ ] CLI script
- [ ] Other / Unknown

## Steps to Reproduce

1. 
2. 
3. 

## Expected Behavior

<!-- What should happen. -->


## Actual Behavior

<!-- What actually happens. Include error messages, tracebacks, or incorrect output. -->

```
paste error or unexpected output here
```

## Input (Anonymized)

<!-- If possible, provide a minimal anonymized example that reproduces the bug.
     Do NOT attach real tender documents. Use synthetic/anonymized data only. -->

**Tender type/sector:** <!-- e.g., "water treatment works tender, ~50 pages" -->

**Company profile snippet (anonymized):**
```json
{
  "company_id": "SAMPLE",
  "annual_turnover_inr_crores": [...],
  ...
}
```

## Environment

- Python version:
- OS:
- anthropic SDK version (`pip show anthropic`):
- Branch/commit:

## Additional Context

<!-- Any other context, screenshots, or log output. -->
