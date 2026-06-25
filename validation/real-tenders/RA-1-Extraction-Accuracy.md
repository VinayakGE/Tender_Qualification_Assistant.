# RA-1 Extraction Accuracy Report

**Sprint:** Reality Acquisition — Sprint 1
**Extraction mode:** Offline (regex only — no ANTHROPIC_API_KEY in test environment)
**Completed:** 2026-06-25

---

## Aggregate Accuracy Table

Across all 10 tenders. "Correct" = extracted value matches the authoritative requirement. "Wrong" = extracted but value incorrect (contaminated or obsolete version). "Missed" = requirement present in document but not extracted. "Absent" = requirement type not present in this tender.

| Requirement Type | Correct | Wrong | Missed | Absent | Accuracy (C/C+W+M) |
|---|---|---|---|---|---|
| Turnover (correct current value) | 6 | 6 | 0 | 0 | 50% |
| Experience (count + value) | 1 | 1 | 7 | 1 | 11% |
| Net worth / financial | 4 | 0 | 2 | 4 | 67% |
| ISO 9001:2015 | 7 | 0 | 0 | 3 | 100% |
| ISO 14001:2015 | 0 | 0 | 3 | 7 | 0% |
| ISO 45001 / other 5-digit | 0 | 0 | 1 | 9 | 0% |
| Registration / enrolment | 0 | 0 | 8 | 2 | 0% |
| Structural eligibility (JV, etc.) | 0 | 0 | 1 | 9 | 0% |
| Domain / work-type requirement | 0 | 0 | 10 | 0 | 0% |

**Notes on turnover "wrong" count:** The 6 "wrong" turnover extractions include accumulated obsolete corrigendum versions (T08: 2 wrong of 3 extracted; T09: 4 wrong of 5 extracted). The authoritative value was extracted in each case but alongside non-authoritative versions. The engine cannot distinguish which is correct.

**Notes on experience "correct" count:** Tender005 extracted a turnover-only tender correctly. Tender004 extracted experience value correctly but domain-blind (the count/value was right, the domain was ignored). Counted T04 as correct extraction with decision-level error, not extraction error.

---

## Extraction Warning Quality

| Metric | Count |
|---|---|
| Tenders where extraction warnings generated | 10 / 10 |
| Warning type seen | "Offline mode: regex extraction only" (all 10) |
| Warnings that correctly identified a real issue | 10 / 10 |
| Warnings that were false alarms | 0 |
| Real extraction issues that were NOT warned about | All pattern-level failures (PAT-003, PAT-004, PAT-005, missed experience) |

**Warning quality assessment:** The one warning generated ("Offline mode: regex extraction only") is consistently correct — regex extraction does have limitations in all 10 cases. However, it is not specific: it does not identify which requirements were missed or which values were contaminated. The warning system currently has 100% precision and ~5% recall (flags the class of problem but not the instances).

---

## Top Extraction Gaps

Ranked by frequency and impact.

| Priority | Gap | Affected Tenders | Impact | Pattern |
|---|---|---|---|---|
| 1 | Experience requirement — count and value | T01, T02, T03, T04, T07, T08, T09 | High | Multiple causes: parenthetical word-forms ("(two)"), domain noun adjacency ("canal"), lakh denomination |
| 2 | Registration / contractor enrolment | T01, T02, T04, T07, T08, T09, T10 | High | No extraction pattern exists. Non-numeric requirement. |
| 3 | Domain / work-type requirement | T01–T10 (all) | High | `Requirement.sector` never populated. Root cause of PAT-001. |
| 4 | 5-digit ISO certifications | T06, T09 | Medium | PAT-004: `\d{4}` regex misses 14001, 45001, 50001. |
| 5 | Requirement version resolution (corrigenda) | T08, T09 | Medium | PAT-003 Subtype B: no document-section awareness. |
| 6 | Cross-clause value isolation (experience ← turnover) | T06, T10 | Medium | PAT-003 Subtype A: no proximity constraint on experience value extraction. |
| 7 | Structural eligibility conditions | T10 | Medium (latent High) | PAT-005: no schema field, no extraction pattern. |
| 8 | Net worth with table line-wrap | T10 | Low | `_NETWORTH_RE` cannot bridge `\n` + non-whitespace (pipe chars) across table column boundary. |

---

## Per-Tender Summary

| Tender | Reqs Extracted | Correct | Wrong | Key Miss |
|---|---|---|---|---|
| T01 | 4 | 2 | 0 | Experience, net worth |
| T02 | 1 | 0 | 0 | Turnover, OEM cert, reg — only 1 extracted total |
| T03 | 0 | 0 | 0 | All — no numeric thresholds in scope |
| T04 | 5 | 3 | 0 | Experience domain (extracted value correct, domain ignored) |
| T05 | 2 | 2 | 0 | Experience (lakh denomination miss) |
| T06 | 5 | 3 | 1 | Experience value (PAT-003 A); ISO 14001, 45001 (PAT-004) |
| T07 | 1 | 1 | 0 | Experience ("canal" noun); CNNL reg |
| T08 | 5 | 1 | 2 | Turnover accumulation (PAT-003 B); experience ("(two)"); CPWD reg |
| T09 | 7 | 1 | 4 | Turnover accumulation 5-way (PAT-003 B); experience ("(two)"); ISO 14001; RVNL reg |
| T10 | 4 | 2 | 1 | Experience (PAT-003 A contaminated to Rs. 40 Cr); JV structural (PAT-005); net worth; reg |
