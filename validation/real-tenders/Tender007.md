# Tender 07

## Source

| Field | Value |
|---|---|
| Portal | GitHub — jayanthmb14/forthepeople seed data (KPPP-CNNL-2026-04-008), constructed as full NIT |
| Tender ID / Reference | CNNL/MYS-DIV/DS/2026-27/007 |
| Issuing Authority | Cauvery Neeravari Nigam Limited (CNNL), Mysuru Irrigation Division, Government of Karnataka |
| Work Description | Desilting of Visvesvaraya Canal — Mysuru Reach (Package DS-07), Chainage Km 96.400 to Km 110.700 (14.3 km). Mechanical and manual desilting, embankment restoration, CC lining repair, cross-drainage structure reconstruction, field channel desilting. |
| Estimated Value | Rs. 4,10,00,000/- (Rs. 4.10 Crore); EMD: Rs. 82,000/- |
| Download URL | Synthetic — constructed from Karnataka seed data (jayanthmb14/forthepeople) |
| Downloaded On | 2026-06-25 |
| Note | Irrigation / canal works domain. New authority (CNNL — Karnataka irrigation parastatal). Domain is adjacent to road construction (civil earthwork, embankments) but categorically distinct (hydraulic/irrigation). Designed to test PAT-001 in the water infrastructure sector. |

## Pipeline Run

```
python scripts/run_pipeline.py \
  --pdf validation/real-tenders/Tender007.pdf \
  --profile examples/Tender-001/company-profile.json
```

| Metric | Result |
|---|---|
| Parser succeeded | Yes |
| Characters extracted | ~7,800 |
| Extraction method | stream |
| Requirements found | 1 |
| Manual edits needed | 0 |
| Recommendation generated | Yes |
| Recommendation | BID |
| Expected Recommendation | NO BID (see Observations) |
| Qualification score | 100/100 |
| Incumbent risk | 20/100 |
| Competitive Strength | 75/100 |
| Execution Risk | 10/100 |
| Value Score | 56/100 |
| Pipeline duration | 0.009 seconds |
| Confidence | 1.00 |
| Extraction mode | Offline (regex only — no ANTHROPIC_API_KEY) |
| extractor_version | v0.1.0 |
| prompt_version | 1.1.0 |
| schema_version | 1.1 |

## Failure Bucket

Bucket: B/C boundary — Extraction and Decision (PAT-001 confirmed)

Decision Impact: **High** — BID on a tender requiring irrigation/canal experience that Apex does not have; immediate disqualification at technical evaluation

Impact Reason: The tender explicitly states "Works involving road embankments, building construction, or drainage of non-irrigation structures shall NOT qualify as similar work." Apex has zero canal/irrigation project experience. All three of Apex's completed projects are road works. Submitting a bid would result in summary rejection at technical evaluation.

## Observations

**What the pipeline extracted:**
1. [turnover] Average Annual Turnover ≥ Rs. 2.0 Crore — CORRECT; company value 43.87 Crore → PASS

**What the pipeline missed:**
- [experience] 1 similar canal/irrigation work ≥ Rs. 1.50 Crore — NOT extracted
- [registration] CNNL/irrigation department contractor registration — NOT extracted
- GST, PAN, EPF/ESIC, pending-litigation undertaking — NOT extracted

**Why the experience requirement was not extracted.** The `_EXPERIENCE_RE` regex matches "successfully completed" or "at least" followed by a count and then one of the keywords: `works?|projects?|road|highway`. The tender text says "successfully completed at least 1 (one) similar canal work or irrigation scheme work." The keyword scan finds "1 (one)" — but "(one)" breaks the count extraction (the pattern `(?:(\w+)\s+\((\d+)\)|(\d+))` expects `word (digit)`, not `digit (word)`). Even if the count were parseable, the next keyword check would find "canal" not "work" immediately after "similar" — "similar canal work" does not match `(?:similar\s+)?(?:works?|...)` because "canal" is inserted between "similar" and "work". The clause was invisible to the extractor.

**This is a new extraction failure mechanism.** Tender004 extracted the experience clause but stripped the domain qualifier (value/count correct, domain blind). Tender007 failed to extract the experience clause entirely — the domain noun "canal" caused the regex to find no match. Both lead to BID 100/100, but through different paths:
- Tender004 path: experience extracted → domain-blind PASS in eligibility checker (Bucket C)
- Tender007 path: experience not extracted → vacuous 100/100 on 1-of-1 requirements (Bucket B leading to Bucket C)

**PAT-001 — observation 5.** Apex (road contractor) evaluated against CNNL canal desilting (irrigation/water domain). Engine: BID. Human: NO BID. The irrigation domain requires canal/hydraulic works experience, not road construction. CNNL explicitly excludes road embankment works from qualifying experience. Same root cause as Tender001–004: domain fit is not evaluated before thresholds.

**PAT-003 not triggered.** Experience clause was not extracted at all (regex found no match). Cross-contamination requires the experience clause trigger to fire first before `_EXPERIENCE_VALUE_RE` runs. Without a trigger, no contamination occurs.

**PAT-002 partial.** Only 1 requirement extracted (turnover), confidence = 1.0 ("1 of 1 mandatory requirements verified"). This is not quite PAT-002 (which requires near-zero extraction with vacuous pass) — here one real requirement was extracted and genuinely passed. But the remaining requirements (experience, registration) are entirely absent from the engine's view. A partial variant of the vacuous-pass dynamic.

**New Bucket B signal.** The experience extraction failure is distinct from all previous extraction misses:
- Tender003: experience not in document (IT digitization — pages scanned, no rupee value)
- Tender004: experience extracted but domain qualifier stripped
- Tender007: experience clause present in document, domain qualifier (noun "canal") prevents regex from matching
This is the first confirmed case where a domain-specific noun adjective within the experience clause causes total extraction failure.

**Domain adjacency observation.** Canal desilting involves civil earthwork and embankment repair — work that shares surface similarity with road construction (earthwork, compaction, slopes). A human reviewer immediately recognises the irrigation context; the engine has no means to distinguish "road embankment" from "canal embankment."

**Human assessment:** NO BID.
- Turnover: 43.87 Crore > Rs. 2 Crore → PASS
- Experience: no canal/irrigation projects → FAIL (road projects explicitly excluded by tender)
- Registration: Class-I Karnataka PWD, no irrigation/CNNL registration → uncertain (Class-I may satisfy Class-II general civil requirement but irrigation-specific endorsement likely missing)
- The tender's own exclusion clause ("road embankments ... shall NOT qualify") makes this an unambiguous NO BID on experience.

## Raw Output

```
Processing: Tender007.pdf
Profile:    company-profile.json

============================================================
RECOMMENDATION: BID
Qualification Score: 100/100
Competitive Strength: 75/100
Incumbent Risk: 20/100
Execution Risk: 10/100
Value Score: 56/100
Confidence: 1.00

Reasoning:
Recommendation: BID. Qualification score: 100/100.
============================================================
```

## Extracted Requirements Detail

| # | Category | Description | Threshold | Correct? |
|---|---|---|---|---|
| 1 | turnover | Average Annual Turnover ≥ Rs. 2.0 Crore (last 3 FYs) | 2.0 INR_crores_annual_average | ✓ correct |
| — | experience | 1 similar canal/irrigation work ≥ Rs. 1.50 Crore (last 5 years) | 1.5 INR_crores_per_project | ✗ missed — "similar canal work" breaks `_EXPERIENCE_RE` keyword match |
| — | registration | CNNL/irrigation dept. Class II contractor registration | — | ✗ missed |

## PAT-001 Log After Tender007

| # | Tender | Domain Required | Company Domain | Engine | Human | Impact |
|---|---|---|---|---|---|---|
| 1 | Tender001 (CRPF BOP) | Building construction (defence) | Road | BID | REVIEW | High |
| 2 | Tender002 (NITA Otis Lift) | Lift AMC / OEM | Road | BID | NO BID | High |
| 3 | Tender003 (NITA Digitization) | IT / digitization | Road | BID | NO BID | High |
| 4 | Tender004 (CRPF Communication) | Communication / networking | Road | BID | NO BID | High |
| 5 | Tender007 (CNNL Canal) | Irrigation / canal works | Road | BID | NO BID | High |
| C1 | Tender005 (BBMP Road) | Road / highway | Road | BID | BID | None |

PAT-001: 5 observations | 1 output-level counterexample | 0 logic-level counterexamples
Sectors: building, lift AMC, IT, communication, irrigation — 5 distinct sectors
Authorities: CRPF (×2), NIT Agartala (×2), CNNL (×1) — 3 distinct authorities
