# DV-1 Plan — Decision Validation

**Sprint:** Decision Validation — Sprint 1
**Status:** Phase 1 active (prospect research) — outreach begins after RA-2.5 results are published
**Prerequisite for outreach:** RA-2.5 complete, Domain Fit Gate confirmed to generalize

## Phased Execution

DV-1 does not wait for RA-2.5 entirely. List-building runs in parallel.

| Phase | Trigger | Activity |
|---|---|---|
| Phase 1 — Research | Now (RA-2.5 in progress) | Build `validation/DV-1/prospect-list.md`: 25 consultants researched, 10 shortlisted. No outreach. |
| Phase 2 — Sector alignment | RA-2.5 results published | Use RA-2.5 failure classes to re-rank shortlist: prioritize consultants whose portfolio covers the weakest sectors. |
| Phase 3 — Outreach and sessions | Shortlist confirmed | Staged waves (see below). Run their tenders through engine before each session. |

**Why research before RA-2.5 completes:** The prospect pool takes time to identify and does not change based on engine results. Which prospects to prioritize does change — that re-ranking waits for Phase 2. Building the pool now means outreach can begin the day RA-2.5 results are published, not weeks later.

**Funnel target:** 30 researched → 10 shortlisted → contact by wave → 10 observed decisions.

The unit of evidence is still the observed decision. A consultant with 30 active clients may yield 3–4 decisions per session. 2 sessions with 3 high-quality decision traces each outweighs 10 generic demos.

### Outreach Waves

Do not contact the shortlist simultaneously. Use staged waves.

| Wave | Prospects | Purpose |
|---|---|---|
| Wave 1 | 3 | Validate the observation process itself: session length, question quality, "human first, engine second" sequence. You may need to refine the protocol before reaching more people. |
| Wave 2 | 5 | Gather enough evidence to identify recurring divergence classes across independent Decision Laboratories. |
| Wave 3 | Only if needed | Close specific evidence gaps that Wave 1 and Wave 2 did not cover. |

**Why staged:** Best prospects should not be spent before the interview protocol is stable. A session with a poor protocol wastes a high-value Decision Laboratory. Wave 1 is cheap to adjust; Wave 2 benefits from whatever Wave 1 taught about the observation process.

---

## Purpose

RA-2.5 answers: does the engine generalize to unseen tenders?

DV-1 asks the next question:

> Does the engine reason the way an experienced decision owner reasons?

This is Stage A of three validation stages. It does not ask whether the product is commercially viable. It does not measure adoption. It asks whether the engine's reasoning sequence — not just its final recommendation — matches how a competent human approaches the same decision.

---

## The Unit of Evidence

The unit of evidence is the **observed decision**, not the organization and not the interview.

A Decision Laboratory is any environment where the Go/No-Go decision is made regularly:

| Decision Laboratory | Decision Owner | Why valuable |
|---|---|---|
| EPC / civil contractor | Bid or Estimation Manager | Direct production environment; high stakes |
| Tender consultancy | Consultant | Sees 50–200 companies; cross-sector patterns |
| Government systems integrator | Proposal Manager | High tender volume; different risk tolerance |
| Engineering consultancy | Business Development Head | Different evaluation criteria than EPC |
| Large contractor | Tender committee | Group decision-making dynamics |

The goal is **10 observed Go/No-Go decisions** across ≥ 3 Decision Laboratories. The decisions may come from 3 organizations or 7 — the count that matters is decisions observed, not organizations contacted.

---

## Evidence Collection Protocol

### Before each session

1. Select a tender the decision owner will evaluate naturally (not a constructed example).
2. Ask them to evaluate it as they normally would, out loud or with notes visible.
3. Do not show the engine output before they have reached their own conclusion.

### During each session

Record in sequence:
- What information did they look for first?
- What did they look for second?
- What caused them to slow down or ask for clarification?
- At what point did they reach a conclusion?
- What was the conclusion and primary reason?

### After they conclude, show the engine output

Record:
- Did the engine's recommendation match?
- Did the engine's primary reason match?
- What did the engine surface that they had not considered?
- What did they consider that the engine did not?
- Any reaction to the engine's confidence score or reasoning text?

### Reasoning Divergence Classification (per decision)

| Class | Definition |
|---|---|
| Same reasoning | Human and engine reached same conclusion via same primary reason |
| Different reasoning, same conclusion | Both say BID or NO_BID, but for different reasons |
| Different reasoning, different conclusion | Diverge on both path and outcome |
| Engine surfaces new signal | Engine raised a factor the human had not considered (regardless of agreement) |

Record the class for every decision. Do not explain divergences during the sprint — classification first, analysis after all 10 are complete.

### Trust vs Correctness (record separately)

Agreement on recommendation does not imply the evaluator would act on the engine output. After showing the engine result, note any of the following:

- "I agree, but I can't present this to my manager without more detail"
- "I agree, but our policy requires a manual review regardless"
- "I agree, but I wouldn't rely on this alone"
- Evaluator skips sections of the engine output without reading them
- Evaluator uses the recommendation but not the reasoning

These are not reasoning failures — the engine may be correct. They are product adoption signals: gaps between correctness and usability that engineering alone cannot close. Record them in the decision log under a separate "adoption signal" field. Do not conflate them with divergence classifications.

---

## The Surprise Log

Maintain a separate `validation/DV-1/surprise-log.md` alongside the decision log.

A surprise in DV-1 is different from a surprise in RA-2.5. Here, surprises include:

- Decision owner uses information the engine has no category for (a factor outside domain, qualification, and commercial fit)
- Decision owner reaches a conclusion before the engine would have enough information
- Decision owner and engine agree on recommendation but for completely incompatible reasons
- Decision owner immediately trusts or immediately dismisses engine output — note why
- Group dynamics change the decision in ways the engine cannot model

These observations may become the seeds of future engineering patterns or product design decisions that no benchmark can anticipate.

---

## Success Criteria

Defined before the sprint starts.

### Proceed to Stage B (Workflow Validation)

- Reasoning agreement rate (same reasoning or different-reasoning-same-conclusion) ≥ 70% across 10 decisions
- Engine surfaces at least one signal the evaluator had not considered in ≥ 3 of 10 decisions
- No systematic reasoning class that the engine cannot represent at all (a class that appears ≥ 3 times and has no corresponding engine capability)

### Revise before Stage B

- Reasoning agreement < 70% — identify the most common divergence class and trace it to an engineering or taxonomy gap
- Engine surfaces new signals in < 3 decisions — engine may be saying what evaluators already know without adding value

### Pause Stage B

- Decision owners consistently ignore or override engine output — trust gap that requires diagnosis before workflow integration
- A reasoning class appears systematically (≥ 4 times) that is outside the engine's architecture — e.g., relationship-based decisions, incumbent knowledge, political factors

---

## What This Sprint Is Not

- **Not a sales process.** No pricing discussion during DV-1. The conversation is "Can I observe you evaluating a real tender?" not "Would you pay for this?"
- **Not a usability test.** DV-1 does not measure whether the interface is good. It measures whether the reasoning is right.
- **Not a customer interview.** Opinions about the product are secondary. The primary data is the observed decision sequence.

---

## Output

1. `validation/DV-1/decision-log.md` — per-decision records: reasoning sequence, engine comparison, divergence class
2. `validation/DV-1/surprise-log.md` — observations outside the standard metrics
3. `validation/DV-1/DV-1-Report.md` — aggregate reasoning agreement rate, divergence classification breakdown, patterns observed
4. `docs/Evidence-Index.md` — updated: Stage A rows moved from "Not Demonstrated" to "Validated" if criteria met
5. `docs/DV-2-Plan.md` — Stage B (Workflow Validation) plan, written only after DV-1 report is complete

---

## Frozen During DV-1

- No engineering changes (Epic 2, taxonomy fixes, PAT-004)
- No scoring adjustments based on observed divergences
- No interface changes to improve impressions during sessions

The freeze applies for the same reason it does in RA sprints: changing the engine mid-sprint contaminates the measurement. A divergence observed in session 3 and fixed before session 7 cannot be attributed to the original engine or the patched one.
