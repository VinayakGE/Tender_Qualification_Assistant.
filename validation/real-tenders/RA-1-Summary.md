# RA-1 Summary Report

**Sprint:** Reality Acquisition — Sprint 1
**Tenders processed:** 10
**Codebase version:** v0.1.0 (frozen — no changes made during sprint)
**Completed:** —

---

## Parser Results

| Metric | Count |
|---|---|
| Parser succeeded | — / 10 |
| Used pdfplumber | — |
| Used stream fallback | — |
| Used OCR fallback | — |
| Complete failure | — |

---

## Extraction Results

| Metric | Count |
|---|---|
| Requirements extracted (any) | — / 10 |
| Tenders with 0 requirements found | — |
| Avg requirements found per tender | — |

---

## Recommendation Results

| Metric | Count |
|---|---|
| Recommendation generated | — / 10 |
| BID | — |
| REVIEW | — |
| NO_BID | — |
| Failed (no recommendation) | — |

---

## Engine vs Human Agreement

| Metric | Count |
|---|---|
| Match | — |
| Mismatch | — |
| N/A (engine failed) | — |
| Agreement rate | — % |

---

## Failure Distribution

| Bucket | Label | Count |
|---|---|---|
| A | Engineering (parser / pipeline) | — |
| B | Extraction (missed clause / wrong value) | — |
| C | Decision (correct extraction, wrong recommendation) | — |

---

## Impact Distribution

| Impact | Count |
|---|---|
| High | — |
| Medium | — |
| Low | — |

---

## Failure Detail

| # | Tender | Bucket | Impact | Description |
|---|---|---|---|---|
| | | | | |

---

## Patterns Observed

<!-- Fill in after reviewing all 10 Tender00N.md files.
     Look for recurring failure types, not one-off surprises. -->

### Document structure patterns
- 

### Extraction patterns
- 

### Decision patterns
- 

---

## Top 5 Engineering Priorities

Ranked by: Impact first, then frequency.

| Priority | Failure type | Bucket | Impact | Affected tenders |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

---

## Evidence Yield

```
High-impact findings
────────────────────  =  ___  / ___  =  ___
Engineering changes proposed
```

**Interpretation:**
- Ratio > 1 — every engineering change is justified by multiple real findings. Good.
- Ratio ≈ 1 — one finding per change. Acceptable.
- Ratio < 0.5 — more changes than findings. Stop. Gather more tenders before engineering.

Recommendation Agreement Rate (first product KPI):

```
Engine == Human
───────────────  =  ___  / 10  =  ___ %
Total Tenders
```

---

## Recommendation

<!-- One paragraph. What does this sprint tell us about what to build next? -->

---

## Decision

- [ ] Open development — proceed to engineering sprint based on priorities above
- [ ] Collect more tenders — sample size too small to prioritize
- [ ] Customer interview first — unclear if these failures matter to real users
