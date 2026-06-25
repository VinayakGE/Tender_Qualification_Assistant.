# PAT-004 — Identifier Extraction Miss

## Status
Observation — not promoted to engineering

## Definition

The certification regex (`_ISO_RE`) captures ISO standard numbers using the pattern `\d{4}` (exactly 4 digits). ISO standards with 5-digit numbers (ISO 14001, ISO 45001, ISO 50001) are structurally unmatchable by this pattern — not a document-specific miss, but a categorical exclusion.

**Affected standards:**
- ISO 14001 (Environmental Management) — 5 digits
- ISO 45001 (Occupational Health & Safety) — 5 digits
- ISO 50001 (Energy Management) — 5 digits
- Any future 5+ digit ISO standard

**Unaffected (4-digit, correctly extracted):**
- ISO 9001 (Quality Management)
- ISO 9002, 9003 (obsolete variants)

The pattern `\bISO\s+(\d{4}(?:[-:]\d{4})?)\b` fails on "ISO 14001:2015" because:
- `\d{4}` matches "1400", leaving "1:2015"
- `\b` word boundary check fails at position after "1400" (next char is "1", a word char)
- Full match fails; standard not extracted

**When it matters:**
If ISO 45001 (OHS) or ISO 14001 (Environmental) is the **only** disqualifying requirement, the engine misses it and recommends BID. Apex Infrastructure holds ISO 14001:2015 but not ISO 45001:2018 — the latter is increasingly required by central infrastructure agencies (NHAI, MoRTH-class contracts).

## Observation Log

| # | Tender | Standards Required | Standards Extracted | Missed | Apex Holds? | Decision Impact |
|---|---|---|---|---|---|---|
| 1 | Tender006 (NHAI NH-66) | ISO 9001:2015, ISO 14001:2015, ISO 45001:2018 | ISO 9001:2015 only | ISO 14001:2015, ISO 45001:2018 | 14001 ✓, 45001 ✗ | None — NO_BID already correct from turnover/net worth |

## Observation Count
1

## Counterexample Count
0

## Appeared In
Tender006

## Bucket
B (Extraction) — structural regex coverage gap, not a parsing failure

## Impact
None in Tender006 (NO_BID correct regardless). **Latent High**: if ISO 45001:2018 is the only unmet requirement in a future tender, the engine would recommend BID incorrectly. This scenario is realistic — ISO 45001 is common in NHAI/highway/PSU contracts, and many smaller contractors (like Apex) do not yet hold it.

## Engineering
None

## Promotion Threshold
≥ 2 independent tenders where a 5-digit ISO standard is required AND either:
  (a) the standard is a pass for the company (hidden pass — harmless but confirms the extraction gap), OR
  (b) the standard is a fail for the company AND the extraction miss changes the recommendation from NO_BID to BID (output impact)

**Note:** Observation (b) is a higher-impact trigger. Track for (a) first to confirm recurrence.

## Notes

**Why this is distinct from PAT-003:**
PAT-003 is about extracted values leaking across clause boundaries (the extraction finds something, but the wrong value). PAT-004 is about categories of identifiers that are structurally excluded from extraction regardless of clause position. Different failure mechanism; different fix.

**Fix direction (not for implementation during RA-1):** Change `\d{4}` to `\d{4,5}` in `_ISO_RE`. One-character fix with no ambiguity — ISO standard numbers are well-defined numeric codes.

**Co-occurrence with PAT-003:** Both appeared in Tender006. They are independent — PAT-003 affects value extraction, PAT-004 affects identifier extraction. A tender can exhibit one without the other.

**Do not build until promotion threshold is met.**
