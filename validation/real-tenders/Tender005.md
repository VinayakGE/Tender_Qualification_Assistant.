# Tender 05

## Source

| Field | Value |
|---|---|
| Portal | GitHub — jayanthmb14/forthepeople (prisma/seed-tenders-karnataka.ts, structured seed data) |
| Tender ID / Reference | KPPP-BBMP-2026-04-001 |
| Issuing Authority | Bruhat Bengaluru Mahanagara Palike (BBMP), Karnataka |
| Work Description | Resurfacing of Arterial Roads — Bituminous Concrete Overlay, Mahadevapura & K.R. Puram (Package 3), BBMP East Zone, Bengaluru |
| Estimated Value | Rs. 1,85,00,000/- (Rs. 1.85 Crore); EMD: Rs. 3,70,000/- |
| Download URL | Synthetic — constructed from Karnataka e-procurement seed data (jayanthmb14/forthepeople) |
| Downloaded On | 2026-06-25 |
| Note | Synthetic document constructed from structured Karnataka procurement seed data. Structurally realistic. 3 pages, 8K. Road resurfacing tender for 12.8 km bituminous concrete overlay. |

## Pipeline Run

```
python scripts/run_pipeline.py \
  --pdf validation/real-tenders/Tender005.pdf \
  --profile examples/Tender-001/company-profile.json
```

| Metric | Result |
|---|---|
| Parser succeeded | Yes |
| Characters extracted | ~3,800 |
| Extraction method | stream |
| Requirements found | 2 |
| Manual edits needed | 0 |
| Recommendation generated | Yes |
| Recommendation | BID |
| Expected Recommendation | BID (see Observations) |
| Qualification score | 100/100 |
| Incumbent risk | 20/100 |
| Competitive Strength | 75/100 |
| Execution Risk | 10/100 |
| Value Score | 52/100 |
| Pipeline duration | 0.010 seconds |
| Confidence | 1.00 |
| Extraction mode | Offline (regex only — no ANTHROPIC_API_KEY) |
| extractor_version | v0.1.0 |
| prompt_version | 1.1.0 |
| schema_version | 1.1 |

## Failure Bucket

Bucket: B (Extraction) — partial miss; no decision failure

Decision Impact: None — correct recommendation despite incomplete extraction

Impact Reason: Engine recommended BID; human assessment is BID. The recommendation is correct. However, the engine extracted only 2 of 4 eligibility items (turnover + ISO 9001:2015), missing the experience requirement (similar road work ≥ Rs. 74 Lakh) and the PWD registration requirement. Apex Infrastructure would pass both missed requirements (NH-48 road widening Rs. 28.5 Crore >> Rs. 74 Lakh; Class-I PWD Karnataka registered), so the extraction miss did not affect the output. Extraction failure, no decision failure.

## Observations

**What the pipeline extracted (offline regex mode):**
1. [turnover] Annual Turnover ≥ Rs. 1 Crore — CORRECT threshold; company value 43.87 Crore → PASS
2. [certification] ISO 9001:2015 — CORRECT; company holds certificate → PASS

**What the pipeline missed:**
- [experience] 1 similar road work ≥ Rs. 74 Lakh (last 5 years) — not extracted; regex does not handle lakh-denomination experience thresholds in this clause format
- [registration] Karnataka PWD Class-I Contractor registration — not extracted

**Human assessment of missed requirements:**
- Experience: NH-48 road widening (Rs. 28.5 Crore), Urban Roads Pune (Rs. 14.2 Crore), MP State Highway (Rs. 11.8 Crore) — all vastly exceed Rs. 74 Lakh threshold → PASS
- Registration: Apex Infrastructure holds Karnataka PWD Class-I registration → PASS

**PAT-001 counterexample analysis.** This was the pre-registered PAT-001 counterexample test: Apex Infrastructure (road contractor) evaluated against a road resurfacing tender (BBMP Karnataka). Engine recommends BID; human agrees — BID.

However, the counterexample is qualified. The engine did not detect domain fit. It reached BID by passing turnover and ISO 9001 — neither involves domain. The experience requirement (similar road work ≥ Rs. 74 Lakh) was not extracted, so the eligibility checker was never invoked for experience. The domain-aware check that would constitute a genuine counterexample — checker matching road projects against road work requirement and returning PASS — did not occur.

What a genuine counterexample to PAT-001 requires: engine extracts an experience requirement, invokes the eligibility checker, checker matches company projects against the required domain and returns PASS, and human agrees with BID. Tender005 does not meet this bar — the checker was not invoked for experience.

Tender005 is nonetheless a counterexample in output terms: engine BID, human BID, road contractor on road tender. PAT-001's counterexample count increments to 1. The observation count remains 4 — this tender does not add a new failure observation.

**PAT-002 not present.** 2 requirements extracted; confidence = 1.0 reflects genuine pass on extracted requirements. The missed experience is a Bucket B miss, not the vacuous-pass dynamic that defines PAT-002.

**New extraction signal (Bucket B).** Rs. 74 Lakh experience threshold not captured by regex. This is the first observation of lakh-denomination experience thresholds eluding extraction. Worth tracking — may recur in lower-value tenders targeting smaller contractors.

## Raw Output

```
Processing: Tender005.pdf
Profile:    company-profile.json

============================================================
RECOMMENDATION: BID
Qualification Score: 100/100
Competitive Strength: 75/100
Incumbent Risk: 20/100
Execution Risk: 10/100
Value Score: 52/100
Confidence: 1.00

Reasoning:
Recommendation: BID. Qualification score: 100/100.
============================================================
```

## Extracted Requirements Detail

| # | Category | Description | Threshold | Correct? |
|---|---|---|---|---|
| 1 | turnover | Annual Turnover ≥ Rs. 1 Crore (last 3 FYs) | 1.0 INR_crores_annual | ✓ correct |
| 2 | certification | ISO 9001:2015 | — | ✓ correct |
| — | experience | 1 similar road work ≥ Rs. 74 Lakh (last 5 years) | 74.0 INR_lakhs, count≥1 | ✗ missed |
| — | registration | Karnataka PWD Class-I Contractor | — | ✗ missed |

## PAT-001 Status After Tender005

| # | Tender | Domain Required | Company Domain | Engine Result | Human Result | Impact | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Tender001 (CRPF BOP Rajasthan) | Building construction (defence) | Road construction | BID | REVIEW | High | 4 reqs extracted |
| 2 | Tender002 (NITA Otis Lift AMC) | Lift AMC / OEM-authorized | Road construction | BID | NO BID | High | 1 req extracted |
| 3 | Tender003 (NITA Digitization) | IT services / digitization | Road construction | BID (0.50 conf) | NO BID | High | 0 reqs extracted |
| 4 | Tender004 (CRPF Communication) | Communication / networking | Road construction | BID | NO BID | High | 5 reqs extracted; checker invoked; domain-blind pass |
| C1 | Tender005 (BBMP Road) | Road / highway | Road construction | BID | BID | None | Output-level counterexample; experience not extracted; checker not invoked |

Observations: 4 | Output-level counterexamples: 1 | Logic-level counterexamples: 0
