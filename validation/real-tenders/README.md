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

| # | Tender ID | Portal | Parser | Extraction | Engine | Expected | Match | Duration |
|---|---|---|---|---|---|---|---|---|
| 1 | — | — | — | — | — | Unknown | — | — |
| 2 | — | — | — | — | — | Unknown | — | — |
| 3 | — | — | — | — | — | Unknown | — | — |
| 4 | — | — | — | — | — | Unknown | — | — |
| 5 | — | — | — | — | — | Unknown | — | — |
| 6 | — | — | — | — | — | Unknown | — | — |
| 7 | — | — | — | — | — | Unknown | — | — |
| 8 | — | — | — | — | — | Unknown | — | — |
| 9 | — | — | — | — | — | Unknown | — | — |
| 10 | — | — | — | — | — | Unknown | — | — |

**Columns:**
- **Engine** — what the pipeline produced (BID / REVIEW / NO_BID)
- **Expected** — your judgment after reading the tender manually (filled in *after* the engine runs)
- **Match** — Yes / No / N/A (N/A when engine failed to produce a recommendation)

Update this table after every run. The table is the sprint deliverable.
