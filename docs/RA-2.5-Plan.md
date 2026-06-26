# RA-2.5 Plan — External Validation

**Sprint:** Reality Acquisition — Sprint 2.5
**Status:** Planned — begins after RA-2 push is reviewed
**Prerequisite:** RA-2 complete ✓

---

## Purpose

RA-2 proved the Domain Fit Gate achieves 100% agreement on the RA-1 benchmark suite.

RA-2.5 answers the question RA-2 cannot answer:

> Does the Domain Fit Gate generalize beyond the 10 tenders and 1 company it was built against?

This is a generalization test, not a performance improvement. No code changes are made during RA-2.5. The gate runs as-is.

---

## What Differentiates RA-2.5 from RA-1 and RA-2

| Dimension | RA-1 / RA-2 | RA-2.5 |
|---|---|---|
| Tenders | 10 (fixed benchmark) | 20–30 (unseen) |
| Company profiles | 1 (Apex, road contractor) | 3–5 (multi-sector) |
| Code changes during sprint | None (RA-1 freeze) | None |
| Purpose | Build benchmark, implement Epic 1 | Test generalization |

---

## Target Portfolio

### Tender Selection (20–30 tenders)

Select tenders to stress-test the gate's domain taxonomy. Priority: cover branches the RA-1 suite under-represents.

| Domain Branch | RA-1 Coverage | RA-2.5 Target (additional) |
|---|---|---|
| road-highway | 3 (T05, T06, T10) | 3–5 more (different authorities: NHDCL, BRO, state PWD) |
| building-construction | 4 (T01, T02, T04, T08) | 2–3 more (NHB, NBCC, non-CPWD) |
| irrigation-canal | 1 (T07) | 2–3 more (CWC, state WRD) |
| bridge-structures | 0 | 2–3 (standalone bridge without railway authority) |
| railway-metro | 1 (T09) | 2 (DMRC, KMRL — metro not ROB) |
| lift-escalator | 1 (T02, labeled as building†) | 2 (OEM-specific, non-NIT authority) |
| it-digitization | 1 (T03, labeled as building†) | 2 (MeitY, NIC — no NIT authority) |
| communication-networking | 1 (T04, labeled as building†) | 2 (BSNL, DoT — no CRPF authority) |

**†** T02, T03, T04 were FAIL'd correctly but labeled as `building-construction` due to NIT/CRPF authority signals. RA-2.5 targets the same domain branches issued by different authorities to test whether label accuracy improves when the conflating authority is absent.

### Company Profile Selection (3–5 profiles)

Each profile must have a clearly defined primary sector. The gate should PASS tenders that match and FAIL those that do not.

| Profile | Primary Sector | Expected Gate Behavior |
|---|---|---|
| Apex Infrastructure (existing) | road-construction → road-highway | Continuity from RA-1 |
| Electrical / MEP contractor | electrical, HVAC, MEP | Should FAIL road, building, IT tenders |
| IT services firm | software / digitization | Should FAIL road, building, lift tenders |
| OEM authorized supplier | lift-escalator | Should PASS lift, FAIL road, IT |
| Structural / bridge contractor | bridge-structures | Should PASS bridge, FAIL irrigation, IT |

---

## Sprint Contract

**No engineering changes during RA-2.5.** The gate runs as-is.

If the domain gate shows systematic failure on a new tender class during RA-2.5, that failure is documented as a new observation — it is not fixed mid-sprint. Fixes happen after RA-2.5 results are published.

---

## Success Criteria

| Criterion | Target |
|---|---|
| Domain Fit Gate output agreement (new tenders) | ≥85% |
| False BIDs on domain-mismatched tenders | ≤15% of mismatched tenders |
| False NO_BIDs on domain-matched tenders | 0 |
| Authority signal conflation rate (T02/T03/T04 pattern) | Documented; not a failure metric |
| UNCERTAIN rate (gate cannot decide) | <20% |

If output agreement drops to 63–70%, the taxonomy needs targeted work before Epic 2 begins. If it holds at 85%+, Epic 2 is the highest-confidence next investment.

---

## What RA-2.5 Is Not

- **Not Epic 2.** No Requirement Resolution code. Not even a minor regex fix.
- **Not a replacement for suite-RA1.** The 10-tender benchmark is not replaced — RA-2.5 creates a new suite (`benchmarks/suite-RA25/`).
- **Not a product launch.** The profiles introduced here are for measurement, not production use.

---

## New Failure Classes to Watch For

Beyond the known gaps (PAT-003, PAT-004, PAT-005), RA-2.5 may surface:

| Candidate failure | Description | How it would appear |
|---|---|---|
| Cross-domain tender | Tender requires multiple work types (road + bridge + building) | Gate gives UNCERTAIN or wrong primary branch |
| Sub-component domain gap | Tender is road, but requires OEM authorization for a sub-component | Gate gives PASS; sub-domain audit misses the disqualifier |
| Authority signal conflation | Authority name contains keywords from wrong domain branch | Gate labels wrong branch (same pattern as T02/T03/T04) |
| JV lead partner requirement | Lead partner must be in specific domain; partner may differ | Gate evaluates company profile only — lead vs partner distinction not represented |
| Framework / rate contracts | No single work type; covers multiple domain branches | Gate uncertain; UNCERTAIN handling becomes important |

---

## Output

After RA-2.5 is complete:

1. `benchmarks/suite-RA25/manifest.md` — tender list, authorities, human verdicts, profile assignments
2. `benchmarks/suite-RA25/results/RA-25.md` — per-tender gate decisions and aggregate metrics
3. `benchmarks/dashboard.md` — updated with RA-2.5 row
4. `docs/RA-3-Plan.md` — Epic 2 plan, unblocked if gate holds at ≥85%

---

## Sequencing Rationale

RA-2 proved the gate works on 10 tenders designed around one road contractor. The gate's taxonomy was also built with those 10 tenders in view — there is some risk of overfit to the benchmark.

RA-2.5 answers: "If we added 20 tenders we had never seen before and 4 company types we had never modeled, does the gate still hold?"

If yes: Epic 2 builds on a stable foundation.
If no: the taxonomy is the bottleneck, and Epic 2 would be wasted effort on top of an unstable gate.

This is the same discipline that governed RA-1 → RA-2. One question at a time, one measurable answer.
