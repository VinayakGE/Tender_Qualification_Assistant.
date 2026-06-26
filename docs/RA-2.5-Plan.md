# RA-2.5 Plan — External Validation

**Sprint:** Reality Acquisition — Sprint 2.5
**Status:** Planned — begins after RA-2 review
**Prerequisite:** RA-2 complete ✓

---

## Purpose

RA-2 proved the Domain Fit Gate achieves 100% agreement on the RA-1 benchmark suite.

RA-2.5 asks the harder question:

> Did we discover a generally useful capability, or did we optimize for our benchmark?

This is a generalization test, not a performance improvement. No code changes are made during RA-2.5. The gate runs as-is on unseen tenders evaluated against multiple company profiles.

---

## Pre-Collection Checklist (complete before sourcing any tender)

The 24 tenders are consciously chosen. Conscious selection creates selection bias risk: tenders may be chosen because they are "interesting," which replicates the same curatorial pattern as RA-1. This checklist is verified before the first tender is collected, and again at the halfway point (after tender 12).

| Dimension | Target | Verify before starting | Verify at tender 12 |
|---|---|---|---|
| Distinct issuing authorities | ≥ 8 | — | — |
| States / territories covered | ≥ 4 | — | — |
| Sector categories | All 5 as designed | — | — |
| OCR / scan quality | Mix: at least 4 scanned/poor-quality PDFs | — | — |
| Tenders with corrigenda | 3–6 | — | — |
| Tenders without corrigenda | Remainder | — | — |
| Contract size (small < Rs. 5 Cr) | ≥ 4 | — | — |
| Contract size (large > Rs. 50 Cr) | ≥ 4 | — | — |
| Tenders evaluated against ≥ 2 profiles | ≥ 6 | — | — |

A tender chosen primarily because it is expected to fail interestingly is a selection bias risk. When in doubt, prefer the less interesting tender.

---

## Challenge Set Design

**24 tenders** across 5 categories. The count is fixed before the sprint starts — no adding tenders after results begin arriving.

| Category | Count | Purpose |
|---|---|---|
| Road / Highway | 6 | Positive controls for Domain Fit — these must still PASS |
| Building / Civil | 6 | Closely related to road but different branch — FAIL for road contractor |
| IT / Digitization | 4 | Test semantic separation from civil domains |
| Lift / Electrical / Communication | 4 | Specifically test the T02–T04 authority-conflation hypothesis: same domains, different authorities than NIT/CRPF |
| Mixed / Edge Cases | 4 | JV-only, consultancy, water treatment, rail — discover new failure modes |

**Selection rule for category 4:** At least 2 of the 4 tenders must come from authorities other than NIT and CRPF. This directly tests whether the T02/T03/T04 label errors were authority-specific or a deeper taxonomy problem.

**Selection rule for category 5:** Each tender in this category should represent a domain not yet in the taxonomy (water treatment, consultancy, geotechnical survey) or a structural condition (JV-only, public-sector-only). These are expected failure modes — the point is to document them, not to pass them.

---

## Company Profiles

The benchmark varies both tenders and companies. The same tender evaluated against different companies is often more diagnostic than another new tender.

| Profile | Primary Sector | Gate expectation |
|---|---|---|
| Apex Infrastructure (existing) | road-construction → road-highway | Road tenders PASS; all others FAIL |
| Building contractor | building-construction | Building tenders PASS; road, IT, lift FAIL |
| IT services firm | it-digitization | IT tenders PASS; road, building, lift FAIL |
| Electrical / MEP contractor | electrical / lift-escalator | Lift/MEP tenders PASS; road, building, IT FAIL |
| OEM / Maintenance provider | lift-escalator (OEM-authorized) | Lift tenders PASS; road, IT FAIL |

A minimum of 3 profiles must be used. All 5 is ideal. Each profile is fixed before the sprint starts.

---

## Evaluation Protocol

The same discipline used in RA-1:

1. **Human verdict written before reviewing engine output.** Evaluator records BID / NO_BID and the primary reason (domain mismatch, threshold fail, structural ineligibility, etc.) before running the pipeline.
2. **No code changes during the sprint.** If a failure is discovered, it is logged. It is not fixed.
3. **All failures classified before any discussion of fixes.** The sprint ends with a complete failure taxonomy, not a partial one with the easy failures already patched.
4. **Delta report written before any implementation begins.** RA-3 is not planned until RA-2.5-Delta-Report.md is complete.

---

## Metrics

Two primary metrics, measured separately:

### 1. Recommendation Agreement

Engine recommendation matches human verdict (BID / NO_BID).

### 2. Branch Label Accuracy (new in RA-2.5)

For each tender, record:
- Expected domain branch (human-assessed from tender text)
- Predicted domain branch (gate's `tender_branch` field)
- Correct / Incorrect

This separates "correct decision via wrong taxonomy" from "correct decision via correct taxonomy." A gate that achieves 90% agreement but 60% branch accuracy is architecturally fragile — it is getting the right answer for the wrong reason, and it will fail when the company profile stops being a road contractor.

### Result Template (per tender)

| Tender | Authority | Human Verdict | Engine Verdict | Output Agreement | Expected Branch | Detected Branch | Branch Correct | Gate Decision | Profile Used |
|---|---|---|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ✓/✗ | ... | ... | ✓/✗ | PASS/FAIL/UNCERTAIN | ... |

### Aggregate Metrics Table

| Metric | RA-2 (suite-RA1) | RA-2.5 (suite-RA25) | Delta |
|---|---|---|---|
| Recommendation agreement | 100% (10/10) | — | — |
| Branch label accuracy | ~70% (7/10)† | — | — |
| False BIDs | 0 | — | — |
| False NO_BIDs | 0 | — | — |
| UNCERTAIN rate | 0% | — | — |
| Gate precision | 100% (7/7) | — | — |
| Gate recall | 100% (7/7) | — | — |

**†** RA-2 branch label accuracy: T01 ✓, T02 ✗ (building vs lift), T03 ✗ (building vs IT), T04 ✗ (building vs comms), T05 ✓, T06 ✓, T07 ✓, T08 ✓, T09 ✓, T10 ✓ = 7/10 = 70%.

---

## Success Criteria

Defined before the sprint starts. Results are measured against these criteria, not adjusted after.

### Pass → Epic 2 unblocked

- Recommendation agreement ≥ 90%
- Branch label accuracy ≥ 90%
- No systematic new failure class (a failure class is "systematic" if it appears ≥ 3 times across unrelated tenders or authorities)
- Domain Fit produces zero false NO_BIDs on positive controls (road tenders evaluated against road contractor)

### Investigate before Epic 2

- Recommendation agreement is high (≥ 85%) but branch label accuracy is low (< 80%) — taxonomy needs targeted work before Epic 2 rests on it
- One new recurring failure class appears (≥ 2 observations, not yet at 3) — document, decide whether to fix or track

### Pause Epic 2

- Recommendation agreement falls materially on unseen data (< 80%)
- Multiple new domain categories consistently fail (≥ 2 failure classes, each with ≥ 3 observations)
- False NO_BIDs appear on domain-matched tenders — gate is misfiring, not just mislabeling

---

## Specific Hypothesis RA-2.5 Must Answer

**The authority-conflation hypothesis:** T02, T03, T04 were FAIL'd correctly but labeled `building-construction` rather than their true branches. The cause: NIT and CRPF are authoritative signals assigned to `building-construction` in the v1 taxonomy, but these bodies issue contracts across multiple domains.

**Test design:** Source at least 2 lift/IT/comms tenders from authorities other than NIT and CRPF. If those tenders now get the correct branch label, the conflation is authority-specific and fixable by moving NIT/CRPF out of `building-construction`'s authoritative signal list. If they still mislabel, the keyword taxonomy itself is the problem.

**Prediction:** The conflation is authority-specific. Lift tenders from Schindler/KONE/municipal authorities will score `lift-escalator` correctly. IT tenders from NIC/MeitY will score `it-digitization` correctly.

If the prediction is wrong, that's the most important finding of RA-2.5.

---

## What RA-2.5 Is Not

- **Not Epic 2.** No Requirement Resolution code. No regex changes. No PAT-004 fix.
- **Not a replacement for suite-RA1.** The 10-tender benchmark remains the primary regression suite. RA-2.5 creates a new suite (`benchmarks/suite-RA25/`) that supplements it.
- **Not a product launch.** The company profiles introduced here are for measurement, not production use.

---

## Output

1. `benchmarks/suite-RA25/manifest.md` — 24 tender list with authorities, categories, human verdicts, profile assignments
2. `benchmarks/suite-RA25/results/RA-25.md` — per-tender results including branch label accuracy
3. `benchmarks/dashboard.md` — updated with RA-2.5 row
4. `validation/real-tenders/RA-2.5-Delta-Report.md` — analysis including authority-conflation hypothesis verdict
5. `docs/RA-3-Plan.md` — Epic 2 plan (written only if success criteria are met)

---

## Frozen Until RA-2.5 Results Are Published

- Epic 2 (PAT-003 Requirement Resolution) implementation
- Any taxonomy changes (even the NIT/CRPF conflation fix)
- PAT-004 fix (`\d{4}` → `\d{4,5}`)
- Any new scoring logic

The freeze is the discipline. RA-2.5 is a measurement sprint, not a development sprint.
