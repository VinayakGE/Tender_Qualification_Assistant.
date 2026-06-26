# Suite RA-1 — Baseline Results (RA-1 Sprint)

**Run date:** 2026-06-25
**Pipeline version:** Pre-Domain-Fit (no gate)
**Domain Fit Gate:** Not implemented
**Notes:** 10 tenders, offline mode (regex extraction only). This is the immutable baseline.

## Per-Tender Results

| Tender | Human Verdict | Engine Verdict | Output Agreement | Engine Primary Reason | Reasoning Agreement |
|---|---|---|---|---|---|
| T01 CRPF BOP | NO_BID | BID | ✗ | Qualification pass (no domain check) | ✗ |
| T02 NIT Lift | NO_BID | BID | ✗ | Qualification pass (no domain check) | ✗ |
| T03 NIT Digitization | NO_BID | BID | ✗ | Qualification pass (no domain check) | ✗ |
| T04 CRPF Comms | NO_BID | BID | ✗ | Qualification pass (no domain check) | ✗ |
| T05 BBMP Road | BID | BID | ✓ | Qualification pass | ✓ |
| T06 NHAI Highway | NO_BID | NO_BID | ✓ | Turnover threshold fail | ✓ |
| T07 CNNL Canal | NO_BID | BID | ✗ | Qualification pass (no domain check) | ✗ |
| T08 CPWD KVS | NO_BID | NO_BID | ✓ | Turnover threshold fail (PAT-003 accumulation) | ✗ (reasoning wrong: PAT-003 drove it, not domain) |
| T09 RVNL ROB | NO_BID | NO_BID | ✓ | Turnover threshold fail (PAT-003 accumulation) | ✗ (reasoning wrong: PAT-003 drove it, not domain) |
| T10 KRDC Highway | NO_BID | NO_BID | ✓ | Experience threshold fail (PAT-003 contamination) | ✗ (reasoning wrong: PAT-003 drove it, not JV mandate) |

## Aggregate Metrics

| Metric | Value |
|---|---|
| Output agreement | 5/10 = **50%** |
| False BIDs (BID / NO_BID mismatch) | **4** (T01, T02, T03, T04, T07) |
| False NO_BIDs (NO_BID / BID mismatch) | **0** |
| Reasoning agreement | 3/10 = **30%** (T05, T06 only — T08/T09/T10 output correct but reason wrong) |
| Domain Fit detection rate | 0/7 = **0%** (gate not implemented) |

## Failure Analysis

| Failure class | Count | Tenders |
|---|---|---|
| PAT-001 (no domain gate) → false BID | 4 | T01, T02, T03, T04, T07 |
| PAT-003 Subtype B (accumulation) → wrong reason | 2 | T08, T09 |
| PAT-003 Subtype A (contamination) → wrong reason | 1 | T10 |
| PAT-005 (JV mandate not detected) → wrong reason | 1 | T10 |
