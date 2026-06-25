# Decision Taxonomy

This taxonomy translates the system's internal failure classifications into language that bid teams understand and can act on.

The internal classification is used in code. The product label is what appears in the recommendation output and any reports.

---

## Taxonomy Table

| Internal Classification | Product Label | Description | Typical Trigger |
|---|---|---|---|
| `qualification_uncertainty` | Missing Eligibility | The system cannot confirm the company meets a stated eligibility requirement — usually because the company profile lacks the relevant information, not because the requirement is definitely unmet | Required field absent from company profile; ambiguous clause in tender |
| `competitive_uncertainty` | Competitive Position Unclear | The system cannot estimate the company's competitive position reliably — usually because the tender type or sector is outside the company's documented experience | Company has no projects in the tender sector; first-time tender type |
| `evidence_gap` | Missing Proof | The company likely meets the requirement based on profile data, but has no documented evidence that could be included in a bid | No ISO certificate on file; no completion certificate for past project |
| `incumbent_risk` | Historical Vendor Dominance | The tender language signals a strong preference for the existing vendor. The current vendor has institutional advantages that make winning unlikely without a compelling differentiator | AMC renewal; "satisfactory performance" language; long existing contracts |
| `scope_mismatch` | Outside Core Capability | The tender requires capabilities, technologies, or sector experience that the company does not have. Not an eligibility disqualifier, but a signal that delivery would be challenging | Required technology stack not in company's service portfolio; unfamiliar sector |
| `financial_threshold_not_met` | Turnover Requirement Gap | The company's annual or average turnover is below the stated threshold | Company turnover ₹20Cr, tender requires ₹30Cr average over 3 years |
| `certification_missing` | Certification Gap | The company does not hold a certification that the tender requires — this is a hard disqualifier if the certification is mandatory | ISO 27001 required, company holds 9001 and 14001 but not 27001 |
| `experience_threshold_not_met` | Experience Requirement Gap | The company has not completed projects of the required value, type, or within the required time window | Tender requires one project >₹5Cr in past 5 years; largest documented project is ₹3.2Cr |
| `net_worth_insufficient` | Net Worth Gap | The company's declared net worth is below the tender's financial soundness requirement | Tender requires net worth ₹10Cr; company net worth is ₹6.5Cr |
| `deadline_risk` | Submission Timeline Risk | The time between tender identification and submission deadline is insufficient for a credible proposal | Tender identified with 5 days to submission; standard preparation takes 10-15 days |
| `multiple_disqualifiers` | Multiple Eligibility Gaps | More than one mandatory requirement is unmet. Each gap is listed separately in `evidence_gaps`. | Company fails turnover, experience, and certification requirements simultaneously |

---

## How Classifications Map to Recommendations

| Classification | Likely Recommendation | Notes |
|---|---|---|
| `financial_threshold_not_met` | NO BID | Hard disqualifier — cannot be overcome without changing facts |
| `certification_missing` | NO BID | Hard disqualifier if mandatory; REVIEW if optional |
| `experience_threshold_not_met` | NO BID or REVIEW | Depends on whether gap is minor (close to threshold) or absolute |
| `net_worth_insufficient` | NO BID | Hard disqualifier |
| `evidence_gap` | REVIEW | Company may qualify; needs to locate and verify evidence |
| `qualification_uncertainty` | REVIEW | Needs manual check before committing |
| `incumbent_risk` | REVIEW | Winnable but should be a conscious decision |
| `competitive_uncertainty` | REVIEW | More information needed before recommending BID |
| `scope_mismatch` | REVIEW or BID | Advisory only; does not block BID unless it affects qualification |
| `deadline_risk` | REVIEW | Flag for bid manager to assess feasibility |
| `multiple_disqualifiers` | NO BID | Any single hard disqualifier triggers NO BID |

---

## Primary Bottleneck Selection

When the recommendation is not a clean BID, the system selects one `primary_bottleneck` from the list of classifications. Selection priority:

1. Hard disqualifiers first (`financial_threshold_not_met`, `certification_missing`, `experience_threshold_not_met`, `net_worth_insufficient`)
2. `evidence_gap` (actionable in the short term)
3. `qualification_uncertainty` (needs human review)
4. `incumbent_risk` (strategic concern)
5. `competitive_uncertainty` (informational)

The `primary_bottleneck` field in the recommendation JSON always uses the **Product Label**, not the internal classification.
