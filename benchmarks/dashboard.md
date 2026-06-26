# Benchmark Dashboard

Last updated: 2026-06-26

## Release Table

| Version | Suite | Change | Output Agreement | False BID | False NO_BID | Branch Label Accuracy | Decision Path Accuracy | Domain Fit Rate |
|---|---|---|---|---|---|---|---|---|
| RA-1 | suite-RA1 | Baseline (no domain gate) | 50% (5/10) | 4 | 0 | n/a | 30% (3/10) | 0% (0/7) |
| RA-2 | suite-RA1 | Domain Fit Gate (Epic 1) | **100% (10/10)** | **0** | 0 | 70% (7/10) † | **90% (9/10)** ‡ | **100% (7/7)** |
| RA-2.5 | suite-RA25 | External validation (no code change) | — | — | — | — | — | — |
| RA-3 | suite-RA1 + suite-RA25 | Requirement Resolution (Epic 2) | — | — | — | — | — | — |

**†** RA-2 branch label accuracy: T02 (lift→building), T03 (IT→building), T04 (comms→building) mislabeled due to NIT/CRPF authority signal conflation. All three FAIL decisions were still correct. 7/10 = 70%.

**‡** RA-2 decision path accuracy: T10 fails — engine cites experience gap (PAT-003) but human verdict is JV mandate (PAT-005). All other 9 tenders: first failing stage matches human reasoning. 9/10 = 90%.

## Suite Index

| Suite | Tenders | Company Profiles | Purpose | Status |
|---|---|---|---|---|
| suite-RA1 | 10 (T01–T10) | 1 (Apex, road contractor) | Primary regression benchmark; all releases measured here | Active |
| suite-RA25 | 24 (balanced challenge set) | 3–5 (road, building, IT, electrical, OEM) | Generalization test; authority-conflation hypothesis; new failure mode discovery | Planned |

## Three Quality Metrics

These three metrics measure different things and are all required. A high score on one does not compensate for a low score on another.

**Output Agreement** — Did we reach the correct decision?
Engine recommendation matches human verdict (BID / NO_BID). Target: ≥90%. A system can achieve high output agreement by being too conservative (rejecting everything) — the false NO_BID rate guards against this.

**Branch Label Accuracy** — Did we understand the opportunity correctly?
Fraction of tenders where the gate's detected domain branch matches the human-assessed true branch. Separates "correct decision via correct taxonomy" from "correct decision via wrong taxonomy." Target: ≥90%. Low label accuracy with high output agreement signals architectural fragility — the system works until the company profile or tender mix changes.

**Decision Path Accuracy** — Did the first failing stage match human reasoning?
For each tender, the stage at which the engine first produces NO_BID (Domain Fit, Qualification, or Scoring) must match the stage a human would cite as the primary reason. Target: ≥90%. Distinguishes correct recommendations that arrived via the right reasoning path from those that arrived by accident.

```
Example: correct path
  Domain Fit → FAIL (engine)     Human: domain mismatch → match ✓

Example: wrong path, same output
  Domain Fit → PASS (engine)     Human: domain mismatch → mismatch ✗
  Qualification → FAIL (engine)
  Recommendation: NO_BID
```

**Supporting metrics**

- False BID: engine BID, human NO_BID. Wastes bid prep. Priority: eliminate.
- False NO_BID: engine NO_BID, human BID. Loses winnable opportunity. Priority: 0 on matched-domain tenders.
- Domain Fit Rate: fraction of mismatched tenders caught by the gate. Tracks gate recall specifically.
- UNCERTAIN rate: fraction of tenders where the gate cannot decide. An UNCERTAIN on a clearly matched tender is a false NO_BID risk.

## Interpretation Notes

- RA-2 100% output agreement is a benchmark result on 10 tenders, 1 company profile. Not a generalization claim.
- suite-RA25 tests generalization under sector diversity (5 company types) and authority diversity (24 unseen tenders).
- Human verdicts are fixed at first run and never revised retrospectively.
- A regression is defined as: any metric on an existing suite declining in a new version without an explicit documented decision to accept the tradeoff.
- Branch Label Accuracy and Decision Path Accuracy were introduced at RA-2. Retroactive RA-1 values are: Branch Label Accuracy = n/a (no gate); Decision Path Accuracy = 30% (same as reasoning agreement — 3/10 tenders had correct output via correct path).
