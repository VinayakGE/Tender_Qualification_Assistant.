# PAT-003 — Clause Cross-Contamination

## Status
Observation — not promoted to engineering

## Definition

The experience value regex (`_EXPERIENCE_VALUE_RE`) has no proximity constraint to the experience clause. It matches the **first** occurrence of any numeric value pattern in the document that satisfies `(?:value|cost|each|not\s+less\s+than).*Rs.*crore`, regardless of whether that match is semantically associated with the experience requirement.

When the turnover clause appears before the experience clause in the document (which is standard NIT format), the experience value is extracted from the turnover clause. The extracted experience threshold is therefore the turnover value, not the actual experience per-project value.

**Mechanism:**
```
Tender text (standard order):
  ...Annual Turnover not less than Rs. 150 Crore...    ← matched first
  ...experience of value not less than Rs. 75 Crore... ← matched second (ignored)

Extracted experience threshold: Rs. 150 Crore (wrong)
True experience threshold:       Rs. 75 Crore (ignored)
```

**When it matters:**
The error is invisible when the wrong (higher) threshold still results in FAIL — Apex fails both Rs. 75 Crore and Rs. 150 Crore. But if the true threshold were ABOVE Apex's profile and the contaminated value were BELOW it, the engine would incorrectly PASS the experience check:

```
Hypothetical: True experience threshold Rs. 50 Crore (Apex max 28.5 Cr → FAIL)
              Contaminated value from turnover Rs. 20 Crore (Apex max 28.5 Cr → PASS)
              Result: BID (wrong)
```

This is the latent high-impact risk from PAT-003.

## Observation Log

| # | Tender | Turnover Clause Value | True Experience Threshold | Extracted Experience Threshold | Correct? | Decision Impact |
|---|---|---|---|---|---|---|
| 1 | Tender006 (NHAI NH-66) | Rs. 150 Crore | Rs. 75 Crore | Rs. 150 Crore (cross-contaminated) | ✗ wrong | None — Apex fails both values |

## Observation Count
1

## Counterexample Count
0

## Appeared In
Tender006

## Bucket
B (Extraction) — the wrong value is extracted, but decision impact depends on the relative magnitudes of the true threshold and the contaminated value.

## Impact
Low in Tender006 (decision unchanged — Apex fails both thresholds). **Latent High**: if the contaminated value is lower than the true threshold and Apex's project value falls between them, the engine will PASS the experience check incorrectly.

## Engineering
None

## Promotion Threshold
≥ 3 independent tenders where cross-contamination occurs AND at least 1 case where the wrong threshold changes the recommendation (output impact, not just extraction impact).

**Note:** Promotion threshold differs from PAT-001/PAT-002 because the extraction error is structural (not semantic). Even 1 confirmed output impact would be sufficient to escalate to engineering.

## Notes

**Root cause:** `_EXPERIENCE_VALUE_RE` is called with `finditer(text)` across the full document. The first match wins regardless of position relative to the experience clause. Standard NIT format always puts turnover before experience, so the contamination is systematic, not occasional.

**Fix direction (not for implementation during RA-1):** Either (a) run `_EXPERIENCE_VALUE_RE` on a windowed substring starting from the `_EXPERIENCE_RE` match position, or (b) replace both with a single combined pattern that requires adjacency.

**Do not build until promotion threshold is met.**
