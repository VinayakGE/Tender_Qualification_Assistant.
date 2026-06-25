# PAT-003 — Clause Cross-Contamination

## Status
Observation — not promoted to engineering

## Definition

The regex extractors share a common structural flaw: all patterns are run independently via `finditer()` across the full document text, with no proximity constraints, no deduplication, and no conflict resolution between multiple matches. This produces two distinct contamination subtypes:

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

| # | Tender | Subtype | Pattern | Extracted (Wrong) | Correct Value | Decision Impact |
|---|---|---|---|---|---|---|
| 1 | Tender006 (NHAI NH-66) | A — Value Cross-Contamination | `_EXPERIENCE_VALUE_RE` | Rs. 150 Cr (from turnover) | Rs. 75 Cr | None — Apex fails both |
| 2 | Tender008 (CPWD KVS) | B — Version Accumulation | `_TURNOVER_RE` | Rs. 25 Cr ×2 (obsolete) + Rs. 50 Cr | Rs. 50 Cr (corrigendum) | None — correct value also extracted; NO_BID driven by Rs. 50 Cr fail |

## Observation Count
2

## Counterexample Count
0

## Appeared In
Tender006, Tender008

## Bucket
B (Extraction) — wrong values extracted or multiple versions accumulated; decision impact depends on relative magnitudes and which version is extracted.

## Impact
- Observation 1 (Subtype A, Tender006): Low — decision unchanged (Apex fails both contaminated and true thresholds). **Latent High**: if contaminated value is lower than true threshold and Apex's profile falls between them, engine incorrectly PASSes.
- Observation 2 (Subtype B, Tender008): Low — correct value was one of three accumulated values; NO_BID driven by the Rs. 50 Crore failure. **Latent High**: if only original pre-corrigendum value were extracted, recommendation would differ depending on direction of amendment.

## Engineering
None

## Promotion Threshold
≥ 3 independent tenders where cross-contamination occurs AND at least 1 case where the wrong threshold changes the recommendation (output impact, not just extraction impact).

**Note:** Promotion threshold differs from PAT-001/PAT-002 because the extraction error is structural. Even 1 confirmed output impact would be sufficient to escalate to engineering.

## Notes

**Subtype A root cause:** `_EXPERIENCE_VALUE_RE` is called with `finditer(text)` across the full document. The first match wins regardless of position relative to the experience clause. Standard NIT format always places turnover before experience, so the contamination is systematic, not occasional.

**Subtype B root cause:** `_TURNOVER_RE` uses `finditer()` with no version resolution. A corrigendum restates the original requirement as context before the amendment, so both appear in the document. The engine treats every match as an independent requirement.

**Fix direction (not for implementation during RA-1):**
- Subtype A: Run `_EXPERIENCE_VALUE_RE` on a windowed substring anchored to the `_EXPERIENCE_RE` match position, or combine into a single proximity-constrained pattern.
- Subtype B: Track document sections (main body vs. corrigendum); when multiple values match the same category and a corrigendum section is present, prefer the amended value.

**Do not build until promotion threshold is met.**
