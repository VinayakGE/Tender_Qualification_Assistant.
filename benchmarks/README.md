# Benchmark Suite

This directory contains the permanent benchmark record for the Tender Qualification Assistant.

## Purpose

Every release answers one question:

> Did this change improve performance on the benchmark without introducing regressions?

This is not a test suite (it does not run automatically). It is a measurement discipline: fixed inputs, fixed human verdicts, measured delta.

## Structure

```
benchmarks/
  suite-RA1/              ← Benchmark suite from RA-1 sprint (10 tenders, 1 profile)
    manifest.md           ← Tender list, authorities, human verdicts
    results/
      RA-1.md             ← Baseline results
      RA-2.md             ← After Domain Fit Gate
      RA-3.md             ← (future)
  suite-RA25/             ← External validation suite (RA-2.5 sprint)
    manifest.md
    results/
      RA-25.md
  dashboard.md            ← Live release table across all suites
```

## How to Add a Result

1. Run all tenders in the relevant suite using the same company profile(s) in the manifest.
2. Record engine output, domain gate decision, and qualification score for each tender.
3. Copy the result template from the most recent `.md` in `results/` and fill in the new column.
4. Update `dashboard.md` with the new row.

Do not edit prior result columns. They are the immutable baseline.

## Measurement Rules

- Same PDF, same company profile, no preprocessing changes between versions.
- Human verdict is fixed at first run and never revised retrospectively.
- "Reasoning agreement" requires both output AND primary reason to match human verdict.
- A benchmark run with a new company profile is a new suite, not an update to an existing one.
