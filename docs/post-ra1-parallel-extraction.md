# Post-RA-1 Design: Parallel Extraction Architecture

**Status:** Not yet built. Implement after RA-1 evidence identifies extraction as a high-impact bottleneck.

---

## Problem this solves

A single Claude call on a 300-page tender is unreliable:
- Context limits force truncation of the document
- One agent is responsible for metadata, eligibility, risk, and documents simultaneously
- A failure in one extraction task contaminates all output
- Debugging requires inspecting one large response

## Proposed architecture

```
Tender PDF (cleaned text)
      │
      ├── Agent 1 → Tender Metadata
      │            (ID, authority, value, EMD, deadlines, duration)
      │
      ├── Agent 2 → Eligibility Requirements
      │            (turnover, experience, financial, certification, equipment,
      │             personnel, JV, registration, statutory)
      │
      ├── Agent 3 → Risk Clauses
      │            (liquidated damages, performance security, penalties,
      │             blacklisting, termination)
      │
      ├── Agent 4 → Required Documents
      │            (bid bond, experience certificates, financial statements,
      │             certifications, declarations)
      │
      └── Agent 5 → Unknowns / Warnings
                   (conflicts, missing annexures, ambiguous clauses,
                    corrigendum references, scanned sections)
```

Each agent receives only the relevant section of the tender text (pre-filtered by `ClauseExtractor`) rather than the full document.

## Output format

```json
{
  "metadata": { ... },
  "requirements": [ ... ],
  "risk_clauses": [ ... ],
  "required_documents": [ ... ],
  "warnings": [ ... ]
}
```

This matches the full `tender.schema.json` contract.

## Before building this

Confirm from RA-1 evidence:

1. Is extraction quality actually a high-impact failure? (Bucket B, High impact, N ≥ 3 tenders)
2. Is the single-agent approach the root cause, or is it the prompt quality / regex fallback?
3. Would section-level pre-filtering by `ClauseExtractor` actually route text to the right agent?

If RA-1 shows that extraction failures are mostly Low impact or are caused by scanned documents
(Bucket A), this architecture solves the wrong problem. Build OCR improvements first.

## Implementation notes

- Each agent uses the same `_call_claude()` infrastructure — just different prompts
- Agents run sequentially (not truly parallel) until we have evidence that latency is a product constraint
- The merge step validates that all five outputs conform to their respective schemas before assembling
- `ExtractionResult.warnings` already propagates to the recommendation output — this architecture just makes warnings richer

## Evidence required to unlock this sprint

From RA-1-Summary.md:
- Bucket B failures ≥ 3 with High impact
- Specific finding that a single-agent context limitation caused the failure
- Evidence that the missed content was present in the PDF text (not a parser problem)
