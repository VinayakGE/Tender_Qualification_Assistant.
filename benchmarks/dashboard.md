# Benchmark Dashboard

Last updated: 2026-06-26

## Release Table

| Version | Suite | Change | Output Agreement | False BID | False NO_BID | Branch Label Accuracy | Domain Fit Rate |
|---|---|---|---|---|---|---|---|
| RA-1 | suite-RA1 | Baseline (no domain gate) | 50% (5/10) | 4 | 0 | n/a (no gate) | 0% (0/7) |
| RA-2 | suite-RA1 | Domain Fit Gate (Epic 1) | **100% (10/10)** | **0** | 0 | 70% (7/10) † | **100% (7/7)** |
| RA-2.5 | suite-RA25 | External validation (no code change) | — | — | — | — | — |
| RA-3 | suite-RA1 + suite-RA25 | Requirement Resolution (Epic 2) | — | — | — | — | — |

**†** RA-2 branch label accuracy: T02 (lift→building), T03 (IT→building), T04 (comms→building) mislabeled due to NIT/CRPF authority signal conflation. All three FAIL decisions were still correct. 7/10 = 70%.

## Suite Index

| Suite | Tenders | Company Profiles | Purpose | Status |
|---|---|---|---|---|
| suite-RA1 | 10 (T01–T10) | 1 (Apex, road contractor) | Primary regression benchmark; all releases measured here | Active |
| suite-RA25 | 24 (balanced challenge set) | 3–5 (road, building, IT, electrical, OEM) | Generalization test; authority-conflation hypothesis; new failure mode discovery | Planned |

## Reading This Table

**Output agreement:** Engine recommendation matches human verdict. Target: ≥90% from RA-2.5 onward.

**False BID:** Engine says BID, human says NO_BID. Wastes bid preparation resources. Priority: minimize.

**False NO_BID:** Engine says NO_BID, human says BID. Loses a winnable opportunity. Priority: keep at 0 on domain-matched tenders.

**Branch Label Accuracy:** Fraction of tenders where the gate's detected domain branch matches the human-assessed true branch. Separates "correct decision for wrong reason" from "correct decision via correct taxonomy." Target: ≥90% from RA-2.5 onward.

**Domain Fit Rate:** Fraction of domain-mismatched tenders correctly FAIL'd by the gate. A gate misfire (FAIL on domain-matched tender) is tracked separately as a false NO_BID.

## Interpretation Notes

- RA-2 100% is a benchmark result on 10 tenders, 1 company profile. It is not a generalization claim.
- suite-RA25 will test whether Domain Fit holds under sector diversity (electrical, IT, OEM, consulting, road) and authority diversity (new authorities not seen in RA-1).
- Each new suite uses fixed human verdicts that are never revised retrospectively.
- A regression is defined as: any metric on an existing suite getting worse in a new version without an explicit decision to accept the tradeoff.
