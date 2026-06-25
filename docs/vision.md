# Vision

## The Problem

Bid teams in government procurement waste 40 to 80 hours per tender — writing proposals, preparing documentation, securing approvals — only to discover at submission that the company never met the eligibility criteria in the first place.

Qualification failures are discovered late because:

1. **Tenders are long and complex.** Government tender documents routinely run 50 to 200 pages, written in legal and technical language. Reading them thoroughly takes hours.
2. **Requirements are scattered.** Turnover thresholds appear in Section 3, certifications in Annexure B, experience requirements in the General Conditions of Contract, and financial criteria in the Bid Data Sheet. No one reads all of it.
3. **Company profiles are not machine-readable.** The knowledge about past projects, certifications, and financials lives in spreadsheets, file folders, and people's heads.
4. **The cost of late discovery is high.** A team that spends a week on a tender that was never winnable has spent real money and opportunity cost on nothing.

This is not a niche problem. Indian government procurement alone runs into hundreds of thousands of tenders per year across central and state levels. Small and medium enterprises — without large bid departments — are the most exposed.

## Mission

**Give every bid team a qualification verdict in under 60 seconds.**

Before a single human hour is committed, the system reads the tender, checks the company profile, and returns a structured answer: bid, review, or no bid.

## Product Vision

A system that:

1. **Reads any tender document** — accepts a PDF from any government portal (CPPP, GeM, state portals), extracts requirements automatically, and structures them into a machine-readable form.

2. **Knows the company** — maintains a living company profile (turnover, certifications, past projects, financial ratios) that is checked against every tender's requirements automatically.

3. **Returns a verdict, not a report** — the first output is a single word: BID, REVIEW, or NO BID. The explanation follows, but the verdict comes first.

4. **Explains every decision** — every score has a traceable source. Every NO BID points to the specific clause that caused it. Nothing is a black box.

5. **Learns from outcomes** — as actual bid results come in, the system can measure its own accuracy and improve over time.

## Success Metrics

The system is working when:

| Metric | Target |
|---|---|
| Time to recommendation | < 60 seconds from PDF drop |
| Qualification accuracy | > 90% match with manual expert review |
| False NO BID rate | < 5% (system should not reject winnable tenders) |
| Coverage | Handles CPPP, GeM, and major state portal formats |
| Decision ledger growth | At least 50 decisions logged in first 3 months |
| Outcome tracking | Actual bid results captured for > 70% of BID recommendations |

## What This Is Not

This is not a proposal writing tool. It does not draft responses, fill bid forms, or prepare tender submissions. Its only job is qualification: should we bid?

Everything downstream of that verdict — writing, pricing, submission — remains human work.
