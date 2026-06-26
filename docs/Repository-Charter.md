# Repository Charter

**Established:** 2026-06-26
**Scope:** All engineering decisions in this repository
**Status:** Permanent — this document does not change

---

This charter governs how engineering decisions are made. It is not about tenders. It applies to any capability built in this repository.

---

## Five Principles

### 1. Engineering follows evidence. It never precedes it.

No feature is built because it sounds useful, looks impressive, or was requested without observation. Every epic begins with a promoted pattern — a failure class observed in real data, classified, and confirmed across multiple independent cases. Implementation is the last step, not the first.

### 2. Benchmarks are immutable once frozen.

A benchmark suite, once established, is never modified to improve a score. Human verdicts are recorded before engine output is reviewed and are never revised retrospectively. A result that looks worse on a fixed benchmark is worse — it cannot be explained away by changing the benchmark.

### 3. New epics require promoted patterns.

A promoted pattern requires: (a) a minimum observation count, (b) independent authorities, (c) at least one confirmed output-level impact. A candidate pattern with one observation does not qualify. The promotion threshold exists to prevent single-case engineering.

### 4. Unknowns are documented with the same discipline as validated claims.

The Evidence Index maintains a "What Has NOT Been Demonstrated" section that is updated alongside the validated sections. A claim that is not in the validated section is a hypothesis, not a fact — even if it seems obvious. The discipline of naming unknowns explicitly is what prevents the repository from quietly overstating what it knows.

### 5. Every release is measured against a fixed benchmark before the next epic begins.

The benchmark is not a gate that blocks work. It is a measurement instrument that makes progress auditable. A release that improves one metric while regressing another has not unambiguously improved — both results must be reported. The release table in `benchmarks/dashboard.md` is the record.

---

## The Development Loop

```
Reality
  ↓
Observation  (real tenders, real decisions)
  ↓
Evidence     (classified failure, bucket, authority)
  ↓
Pattern      (promoted when threshold met)
  ↓
Benchmark    (frozen suite, human verdicts)
  ↓
Engineering  (one epic, one measurable change)
  ↓
Benchmark    (same suite, measured delta)
  ↓
Evidence     (what improved, what didn't, what's still unknown)
```

Each cycle produces one validated claim and one updated Evidence Index. The loop does not skip steps.

---

## What This Rules Out

- Building a feature because a similar product has it
- Declaring success before re-running the benchmark
- Fixing a bug mid-sprint to avoid recording a failure
- Implementing two epics simultaneously and attributing improvement to either one
- Removing or softening the "What Has NOT Been Demonstrated" section

---

## The Rule That Prevents Roadmap Inflation

> Every future epic must move something from "Not Demonstrated" to "Validated."

If an epic cannot point to a row in the Evidence Index that it will promote, it does not belong in the roadmap.
