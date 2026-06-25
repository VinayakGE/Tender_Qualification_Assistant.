# PAT-003 — Requirement Resolution Failure

## Status
**Promoted — engineering queued post-RA-1**

## Definition

The pipeline produces **candidate requirements** — raw matches from regex patterns — but has no **resolution** stage. It treats every match as an independent, authoritative requirement. When the same requirement appears in multiple document locations (table, corrigendum original, corrigendum amended), or when a value from one clause contaminates another, the pipeline accumulates all candidates as peers and passes them all to qualification with equal weight.

The missing capability is a resolver: a stage that takes candidate requirements and determines which version governs. Without it, the pipeline cannot handle corrigenda, duplicate clauses, or cross-clause value contamination correctly.

**Pipeline gap (current vs. needed):**
```
Current:    PDF → Candidate Requirements → Qualification
Needed:     PDF → Candidate Requirements → Requirement Resolution → Canonical Requirements → Qualification
```

All regex patterns share the root cause: `finditer()` across the full document text with no proximity constraints, no deduplication, and no conflict resolution. Two distinct failure subtypes have been observed:

**Subtype A — Value Cross-Contamination (Tender006)**
`_EXPERIENCE_VALUE_RE` matches the **first** occurrence of any numeric value pattern in the document regardless of semantic association. When the turnover clause appears before the experience clause (standard NIT format), the turnover value is extracted as the experience threshold.

```
Tender text (standard order):
  ...Annual Turnover not less than Rs. 150 Crore...    ← matched first (wrong)
  ...experience of value not less than Rs. 75 Crore... ← matched second (ignored)

Extracted experience threshold: Rs. 150 Crore (wrong)
True experience threshold:       Rs. 75 Crore (ignored)
```

**Subtype B — Version Accumulation (Tender008)**
`_TURNOVER_RE` matches every occurrence of "Annual Turnover" + value in the document. When a corrigendum amends a threshold, both the original value (stated in the main table AND restated in the corrigendum "Original requirement" block) and the amended value are all extracted as separate requirements. The engine has no mechanism to identify which version is authoritative.

```
Tender text (with corrigendum):
  Table 1: ...Annual Turnover not less than Rs. 25 Crore...    ← match 1 (obsolete)
  Corrigendum: Original: ...Annual Turnover not less than Rs. 25 Crore... ← match 2 (obsolete)
  Corrigendum: Amended:  ...Annual Turnover not less than Rs. 50 Crore... ← match 3 (correct)

Extracted: [Rs. 25 Crore, Rs. 25 Crore, Rs. 50 Crore] — engine cannot determine authority
Correct:   Rs. 50 Crore (corrigendum supersedes)
```

**Root cause (shared):** `finditer()` with no positional awareness, no document-section tracking, and no supersession logic. Each extractor sees a flat string, not a structured document.

**When each subtype matters:**
- Subtype A: invisible when contaminated value still fails; dangerous when contaminated value (from turnover) is lower than true threshold and would incorrectly PASS
- Subtype B: invisible when the correct amended value is one of the accumulated matches AND it fails; dangerous when corrigendum lowers a threshold and only the original (higher) value is extracted — engine recommends NO_BID when BID is correct; or when only the original value is extracted and it passes, while the corrigendum-raised threshold actually fails — engine recommends BID when NO_BID is correct

## Observation Log

| # | Tender | Authority | Subtype | Accumulation Result | Authoritative Value | Decision Impact |
|---|---|---|---|---|---|---|
| 1 | Tender006 (NHAI NH-66) | NHAI | A — Value Cross-Contamination | Rs. 150 Cr from turnover as experience | Rs. 75 Cr (experience) | None — Apex fails both |
| 2 | Tender008 (CPWD KVS) | CPWD | B — Version Accumulation (1 corrigendum) | [Rs. 25 Cr ×2, Rs. 50 Cr ×1] | Rs. 50 Cr (Corr. 1 amended) | None — correct value also extracted |
| 3 | Tender009 (RVNL ROB) | RVNL | B — Version Accumulation (2 corrigenda) | [Rs. 55 Cr ×2, Rs. 30 Cr ×1, Rs. 50 Cr ×2] | Rs. 55 Cr (Corr. 2 amended) | None — correct value also extracted; 4 of 5 candidates fail |

**Accumulation scaling:** 1 corrigendum → 3 candidates (Tender008); 2 corrigenda → 5 candidates (Tender009). Growth is approximately 2N+1 where N = number of corrigenda.

## Observation Count
3

## Counterexample Count
0

## Appeared In
Tender006, Tender008, Tender009

## Bucket
B (Extraction / Pre-resolution) — resolution stage does not exist; pipeline accumulates candidates without determining which governs. Decision impact depends on relative magnitudes of accumulated values and which version(s) happen to be extracted.

## Impact
- Observation 1 (Subtype A, Tender006): Low — decision unchanged (Apex fails both contaminated and true thresholds). **Latent High**: if contaminated value is lower than true threshold and Apex's profile falls between them, engine incorrectly PASSes.
- Observation 2 (Subtype B, Tender008): Low — correct amended value was one of three accumulated turnover candidates; NO_BID driven by Rs. 50 Crore failure (Apex 43.87 < 50). **Latent High**: if the corrigendum had LOWERED the threshold and only the original (higher) value were extracted, engine could recommend NO_BID when BID is correct — or vice versa.

## Engineering
Queued — implementation post-RA-1 completion and RA-1-Summary.md

**Engineering direction (candidate):**
The fix requires adding a Requirement Resolution stage between extraction and qualification:

```
Current:  PDF → Candidate Requirements → Qualification
Needed:   PDF → Candidate Requirements → Requirement Resolution → Canonical Requirements → Qualification
```

Resolver responsibilities:
- Subtype A: windowed search — run `_EXPERIENCE_VALUE_RE` on a substring anchored to the `_EXPERIENCE_RE` match position, not the full document
- Subtype B: document-section tagging — detect corrigendum blocks; when multiple candidates in the same category exist and a corrigendum section is present, prefer the candidate from the latest corrigendum section
- Both subtypes: deduplication — when two candidates have identical category + threshold, collapse to one

**Do not implement during RA-1.**

## Promotion Threshold
≥ 3 independent tenders exhibiting resolution failure under at least 2 different authorities.

**Threshold met:** 3 observations (Tender006, Tender008, Tender009), 3 authorities (NHAI, CPWD, RVNL), 2 subtypes (A and B). Promoted.

## Notes

**Subtype A root cause:** `_EXPERIENCE_VALUE_RE` is called with `finditer(text)` across the full document. The first match wins regardless of position relative to the experience clause. Standard NIT format always places turnover before experience, so the contamination is systematic, not occasional.

**Subtype B root cause:** `_TURNOVER_RE` uses `finditer()` with no version resolution. A corrigendum restates the original requirement as context before the amendment, so both appear in the document. The engine treats every match as an independent requirement.

**Fix direction (not for implementation during RA-1):**
- Subtype A: Run `_EXPERIENCE_VALUE_RE` on a windowed substring anchored to the `_EXPERIENCE_RE` match position, or combine into a single proximity-constrained pattern.
- Subtype B: Track document sections (main body vs. corrigendum); when multiple values match the same category and a corrigendum section is present, prefer the amended value.

**Do not build until promotion threshold is met.**
