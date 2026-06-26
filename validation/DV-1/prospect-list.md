# Decision Laboratory Prospect List

**Phase:** Pre-DV-1 — Research only. No outreach until RA-2.5 completes.
**Purpose:** Evidence acquisition pipeline. Not a sales pipeline.

Success is measured by:
- Decision Laboratories identified
- Decisions observed
- Reasoning traces collected
- New divergence classes discovered

Every prospect is evaluated by one question: *Will talking to this person increase the quality of evidence available to improve the decision engine?*

Last updated: 2026-06-26

---

## Sector Targets

| Segment | Target Count | Why |
|---|---|---|
| Tender consultants | 8 | Cross-sector patterns; one consultant may expose 30+ client contexts |
| EPC contractors | 7 | Direct production environment; high-stakes decisions |
| Government IT / Systems Integrators | 5 | IT branch weakest in RA-2 taxonomy; likely to surface new divergence classes |
| MEP / Electrical contractors | 5 | Tests lift-escalator and electrical branches; authority-conflation hypothesis |
| Infrastructure specialists (rail, water, highways) | 5 | Multi-authority exposure; different risk tolerance than EPC |
| **Total** | **30** | |

Diversity across these five segments prevents accidentally interviewing five people who think about the same class of tenders.

---

## Prospect List

| # | Company | Decision Owner | Title | Sector | Typical Tender Volume | Portfolio Diversity | Evidence Potential | Evidence Gap Coverage | Contact | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | | Research | |
| 2 | | | | | | | | | | Research | |
| 3 | | | | | | | | | | Research | |

---

## Column Definitions

**Portfolio Diversity** — breadth of tender types the person evaluates regularly.
- Low: single sector (roads-only, buildings-only)
- Medium: 2–3 sectors, same broad category (civil works)
- High: 4+ sectors or cross-category (civil + IT + rail)

Different from Evidence Potential. A High-diversity prospect exposes multiple reasoning patterns per session. A Medium-diversity prospect may still have High Evidence Potential if their sector is one the engine handles poorly.

**Evidence Potential** — likelihood this person's decisions will expose reasoning divergences or new patterns.
- Low: sector the engine handles well; decisions likely to confirm, not challenge
- Medium: some divergence likely; useful for confirmation
- High: sector is weak in current taxonomy, or cross-authority, or involves structural conditions (JV-only, public-sector-only)

**Typical Tender Volume** — estimate of how many Go/No-Go decisions this person makes per year. A consultant with 40 clients making 5 decisions each = 200 tenders/year. That's the leverage that makes consultants the priority segment.

**Evidence Gap Coverage** — which named unknowns from `docs/Evidence-Index.md` ("What Has NOT Been Demonstrated") this prospect is positioned to help validate. This changes the shortlisting question from "Is this a good prospect?" to "Which hypothesis does this prospect help test?"

Examples:

| Prospect type | Evidence Gap Coverage |
|---|---|
| Railway tender consultant | Branch Label Accuracy on rail tenders; authority-conflation hypothesis |
| GeM / Government IT consultant | IT domain taxonomy; PAT-003 Requirement Resolution in IT context |
| EPC bid estimator | Domain Fit Gate reasoning; Decision Path Accuracy |
| MEP / Electrical contractor | Lift-escalator and electrical domain vocabulary; PAT-005 structural eligibility |
| Government IT / SI firm | IT taxonomy sufficiency; structural eligibility (public-sector-only conditions) |
| Large multi-sector consultancy | Engine reasoning vs. experienced decision owner reasoning (DV-1 Stage A) |

A prospect with no clear evidence gap mapping is low priority regardless of other scores.

---

## Evidence Potential Guide

| Profile | Portfolio Diversity | Evidence Potential | Reason |
|---|---|---|---|
| Roads-only consultant | Low | Medium | Positive control; confirms engine works, won't expose new classes |
| Multi-sector EPC consultant | High | High | Different domain reasoning in same session; cross-authority exposure |
| GeM / Government IT procurement | Low | High | IT branch weakest in RA-2; likely to surface mislabeling and new signals |
| Railway / Metro specialist | Low | High | Authority-conflation hypothesis; different reasoning pattern than civil |
| Defence / CPWD specialist | Low | Medium | Narrow domain; similar reasoning to roads |
| Large multi-sector consultancy (50+ clients) | High | High | Volume + diversity; richer pattern exposure per session |
| MEP / Electrical specialist | Low | High | Lift-escalator branch underrepresented in RA-2 |

---

## Stopping Rule

Research stops when all three conditions are met:

1. **30 qualified prospects** researched (all columns populated, Status ≠ blank)
2. **All five sector targets** met (8 / 7 / 5 / 5 / 5 minimums reached)
3. **Every current evidence gap** mapped to ≥ 2 prospects

Without a stopping rule, research expands indefinitely. These three conditions together mean the prospect pool is both complete and hypothesis-driven. At that point, further research has diminishing returns — the constraint shifts to RA-2.5 results and outreach execution.

---

## Funnel Tracker

| Stage | Target | Actual |
|---|---|---|
| Researched | 30 | 0 |
| Shortlisted | 10 | 0 |
| Contacted | 5 | 0 |
| Replied | — | 0 |
| Sessions scheduled | 3 | 0 |
| DV-1 decisions observed | 10 | 0 |
| Reasoning traces collected | 10 | 0 |
| New divergence classes discovered | — | 0 |
| Evidence gaps covered (≥2 prospects each) | All current unknowns | 0 |

---

## Shortlist Criteria

A prospect moves from Research → Shortlisted when:

1. **Sector coverage** aligns with RA-2.5 failure classes (fill in after RA-2.5 results publish)
2. **Portfolio Diversity** = Medium or High (avoid all-same-sector shortlist)
3. **Evidence Potential** = High (at least 7 of the 10 shortlisted)
4. **Tender volume** ≥ 20/year (enough decisions to observe a pattern, not a single-bid context)
5. Direct contact available (LinkedIn, company website, known referral)

Do not shortlist based on convenience. A prospect who is easy to reach but covers only a sector the engine already handles well is a low-return session.

---

## Session Prep Protocol (for when outreach begins — Phase 3)

Before each confirmed session:

1. Ask the consultant for 2–3 tenders they evaluated recently. Redact confidential details if needed.
2. Run those tenders through the engine before the meeting. Record output privately.
3. During the session: let them walk through their reasoning first. Do not show engine output.
4. After they conclude: show engine output, compare step by step.

Record per session:
- Reasoning sequence (what did they look for first, second, what caused them to slow down)
- Conclusion and primary reason
- Engine vs. human: recommendation agreement
- Engine vs. human: reasoning agreement (same class / different reasoning same conclusion / different conclusion)
- New signals surfaced by engine that evaluator had not considered
- Trust observations (agreed but wouldn't act, skipped sections, wouldn't present to manager)
