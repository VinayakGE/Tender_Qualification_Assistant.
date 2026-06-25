# Sprint RA-1 — Reality Acquisition

Run 10 real Indian government tenders through the pipeline unchanged.
Record outcomes here. Do not fix anything between tenders.

## Protocol

1. Download tender PDF from a public portal (CPPP, GeM, state e-procurement).
2. Run the pipeline exactly as downloaded — no edits, no pre-processing.
3. Fill in the corresponding Tender00N.md file.
4. Move to the next tender.

## Rule: No Engineering Between Tenders

If Tender #3 fails the parser, record it and continue to Tender #4.
Pattern analysis happens after all 10 are complete.

## Tracking Table

| # | Tender ID | Portal | Parser | Extraction | Engine | Expected | Match | Bucket | Impact |
|---|---|---|---|---|---|---|---|---|---|
| 1 | — | — | — | — | — | Unknown | — | — | — |
| 2 | — | — | — | — | — | Unknown | — | — | — |
| 3 | — | — | — | — | — | Unknown | — | — | — |
| 4 | — | — | — | — | — | Unknown | — | — | — |
| 5 | — | — | — | — | — | Unknown | — | — | — |
| 6 | — | — | — | — | — | Unknown | — | — | — |
| 7 | — | — | — | — | — | Unknown | — | — | — |
| 8 | — | — | — | — | — | Unknown | — | — | — |
| 9 | — | — | — | — | — | Unknown | — | — | — |
| 10 | — | — | — | — | — | Unknown | — | — | — |

**Columns:**
- **Engine** — what the pipeline produced (BID / REVIEW / NO_BID / FAILED)
- **Expected** — your judgment after reading the tender manually; filled in *after* the engine runs to prevent anchoring
- **Match** — Yes / No / N/A (N/A when engine failed to produce a recommendation)
- **Bucket** — A (Engineering) / B (Extraction) / C (Decision); leave blank if no failure
- **Impact** — High / Medium / Low; how much would this failure cost on a real bid?

Update this table as you go. The completed table plus `RA-1-Summary.md` are the sprint deliverables.

## Exit Condition

All 10 rows filled → complete `RA-1-Summary.md` → present to product review board before reopening development.
