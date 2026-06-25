# Product Principles

Five principles guide every design and implementation decision in this system.

---

## 1. Verdict First

**Lead with BID / REVIEW / NO BID before any explanation.**

The recommendation is the product. Everything else — scores, bottlenecks, reasoning — is supporting evidence for the verdict. When a user opens a result, the first thing they see is the decision, not a wall of analysis.

This applies to the API response, any dashboard display, and any exported report. The recommendation field is always first.

*Why this matters:* Bid managers are time-pressed. They need to know within seconds whether to keep reading or move on. Burying the verdict under scores and caveats forces them to read everything before they know if the tender is even relevant.

---

## 2. Evidence Over Opinion

**Every score has a traceable source. No score is generated without reference to a specific requirement, clause, or company data point.**

When the system says qualification_score = 72, it must be able to show exactly which requirements contributed to that score, which ones were met, and which ones were not. When it says incumbent_risk = 80, it must point to the specific language in the tender that triggered that assessment.

*Why this matters:* Bid teams will push back on a NO BID recommendation if they do not trust the basis. Traceability is what makes the system defensible. It also makes errors findable — when the system gets something wrong, you can see exactly where the reasoning broke down.

---

## 3. Fail Fast

**Surface NO BID in seconds, not hours. A disqualifying condition should terminate the pipeline immediately.**

If a tender requires ISO 27001 and the company does not have it, the recommendation is NO BID. There is no reason to compute competitive strength, incumbent risk, or execution risk. The pipeline should short-circuit as soon as a mandatory disqualifying condition is found.

*Why this matters:* The economic value of the system is in reclaiming time. A NO BID that takes 30 minutes to produce saves nothing. A NO BID that takes 10 seconds saves the entire 40-80 hours that would otherwise be wasted.

---

## 4. Auditable

**Every decision is logged with its reasoning. The ledger is permanent and append-only.**

Every recommendation — BID, REVIEW, or NO BID — is written to `decision-ledger.json` with a timestamp, the input IDs, all five scores, the bottleneck classification, and the reasoning text. Nothing is deleted. When actual outcomes come in, they are linked back to the original recommendation.

*Why this matters:* Over time, the ledger becomes the most valuable artifact in the system. It shows where the system's predictions matched reality and where they did not. It creates accountability — if a team bids a tender the system flagged as NO BID and loses, that decision is on record. It also enables future accuracy measurement and model improvement.

---

## 5. Simple Inputs

**A PDF and a company profile JSON — nothing else required to start.**

The minimum viable workflow is: drop a tender PDF into `data/incoming/`, have a company profile in `data/company-profiles/`, and get a recommendation out. No portal credentials, no database setup, no API integrations, no manual data entry beyond the initial profile creation.

*Why this matters:* Complex setup kills adoption. If the system requires a week of configuration before it produces its first result, most potential users will abandon it before seeing value. The folder-drop trigger is specifically designed so that someone with zero technical knowledge can use the system by following three sentences of instructions.
