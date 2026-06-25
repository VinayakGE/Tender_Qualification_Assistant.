# Scoring Model

All five scores are on a 0-100 scale. Higher is always better from the bidder's perspective — a higher qualification score means a stronger fit, a higher value score means a more attractive opportunity.

The single exception is incumbent risk: a high incumbent risk score (70+) means the existing vendor is likely to be retained, which is *bad* for the bidder. This inversion is explicit and documented in the recommendation engine logic.

---

## 1. Qualification Fit Score

**Range:** 0-100  
**Source:** `src/scoring/qualification_score.py`

### Formula

```
mandatory_met     = count of mandatory requirements with status PASS
mandatory_total   = total mandatory requirements
optional_met      = count of optional requirements with status PASS
optional_total    = total optional requirements (0 if none)

mandatory_score   = mandatory_met / mandatory_total * 100
optional_score    = optional_met / optional_total * 100  (or 100 if no optional reqs)

qualification_score = (mandatory_score * 2 + optional_score * 1) / 3
```

Mandatory requirements are weighted 2x because failing a mandatory requirement is a hard disqualifier in most Indian government tenders. Optional requirements contribute to the score but cannot cause a FAIL.

### Thresholds

| Score | Category | Interpretation |
|---|---|---|
| 0-59 | FAIL | Company does not meet the basic eligibility bar |
| 60-79 | MARGINAL | Borderline pass — likely has gaps that need to be addressed |
| 80-100 | PASS | Meets eligibility criteria; proceed to competitive assessment |

A score below 60 triggers an immediate NO BID regardless of other scores.

---

## 2. Competitive Strength Score

**Range:** 0-100  
**Source:** `src/scoring/competitiveness.py`

### Formula

```
size_factor      = min(company_turnover / contract_value, 3.0) * 20   (max 60)
experience_match = (matching_sector_projects / tender_sector_weight) * 25  (max 25)
capacity_factor  = min(company_employees / min_required_team, 2.0) * 7.5  (max 15)

competitive_strength = min(size_factor + experience_match + capacity_factor, 100)
```

Where:
- `size_factor` rewards companies whose turnover is substantially larger than the contract (signals capacity without being too small)
- `experience_match` rewards sector-specific experience relative to the tender's sector requirements
- `capacity_factor` rewards staffing capacity

This is a *relative* score — it estimates how the company compares to a typical bidder pool for this contract type and size, not an absolute capability measure.

### Thresholds

| Score | Interpretation |
|---|---|
| 0-39 | Weak competitive position — likely outclassed by other bidders |
| 40-64 | Moderate position — competitive but not dominant |
| 65-100 | Strong position — likely among top bidders for this opportunity |

---

## 3. Incumbent Risk Score

**Range:** 0-100  
**Source:** `src/scoring/incumbent_risk.py`

### Formula

This score is heuristic-based, derived from language signals in the tender document:

```
base_score = 20  (all tenders have some baseline continuity bias)

signal_adjustments:
  + 25  if tender contains "satisfactory performance" phrases
  + 20  if tender contains "existing vendor" or "present service provider"
  + 20  if it is an AMC / maintenance / renewal tender type
  + 15  if tender mentions "continuity of service" requirements
  + 10  if contract duration > 3 years (long contracts favor incumbents)
  - 10  if tender was recently re-tendered after cancellation (signals dissatisfaction)
  - 15  if tender explicitly states "new vendors preferred" or has evaluation criteria penalizing incumbents

incumbent_risk = min(base_score + sum(signal_adjustments), 100)
```

### Thresholds

| Score | Interpretation |
|---|---|
| 0-39 | Low incumbent risk — open competition likely |
| 40-69 | Moderate risk — incumbent may have advantage but competition is real |
| 70-100 | High risk — incumbent strongly favored; winning is possible but difficult |

A score of 70+ triggers a REVIEW rather than BID, even when all other conditions are met. This is a deliberate conservative threshold — teams should consciously decide to bid against a strong incumbent rather than have the system recommend it blindly.

---

## 4. Execution Risk Score

**Range:** 0-100  
**Source:** `src/scoring/execution_risk.py`

### Formula

```
timeline_risk    = sigmoid(contract_duration_months / 6) * 20   (max 20)
scope_complexity = count_complexity_keywords(tender_text) * 3    (max 30, capped)
capacity_risk    = max(0, 1 - (company_employees / estimated_team_size)) * 25  (max 25)
experience_gap   = (unfamiliar_sector_requirements / total_requirements) * 25  (max 25)

execution_risk = min(timeline_risk + scope_complexity + capacity_risk + experience_gap, 100)
```

Complexity keywords: "integration", "interoperability", "migration", "transformation", "multi-site", "24x7", "SLA", "penalty clause", "liquidated damages", "performance bond", "bank guarantee".

### Thresholds

| Score | Interpretation |
|---|---|
| 0-29 | Low execution risk — standard scope, adequate capacity |
| 30-54 | Moderate risk — requires careful resourcing and planning |
| 55-100 | High risk — delivery challenge; requires explicit mitigation plan |

Execution risk does not directly feed the BID/REVIEW/NO BID decision in MVP. It is surfaced as a signal for the bid team and contributes to the value score.

---

## 5. Value Score

**Range:** 0-100  
**Source:** `src/scoring/value_score.py`

### Formula

```
contract_value_score  = log_scale(contract_value_inr, min=1L, max=100Cr) * 35  (max 35)
strategic_fit_score   = sector_priority_match(tender_sector, company_priority_sectors) * 30 (max 30)
win_probability_score = estimate_win_prob(qualification_score, competitive_strength, incumbent_risk) * 35  (max 35)

value_score = contract_value_score + strategic_fit_score + win_probability_score
```

Where:
- `contract_value_score` uses a logarithmic scale so very large contracts don't dominate (₹1L to ₹100Cr mapped to 0-35)
- `strategic_fit_score` is based on the company profile's `priority_sectors` list — a perfect match scores 30, no match scores 0
- `win_probability_score` is derived from the three input scores: higher qualification + higher competitiveness + lower incumbent risk = higher win probability estimate

### Thresholds

| Score | Interpretation |
|---|---|
| 0-39 | Low value opportunity — marginal contract value and/or poor win probability |
| 40-64 | Moderate value — worth pursuing if qualification is strong |
| 65-100 | High value — strong strategic and/or financial case to bid |

Value score is an advisory signal, not a gate. A high-value tender with qualification FAIL still receives NO BID. A low-value tender with clean qualification may still receive BID.

---

## Score Interactions

The five scores feed the recommendation engine as follows:

```
qualification_score     → gates BID/NO BID (primary gate)
incumbent_risk          → downgrades BID to REVIEW at 70+
evidence_gaps           → downgrades BID to REVIEW when critical gaps present
competitive_strength    → contributes to confidence score
execution_risk          → surfaced as advisory; contributes to confidence score
value_score             → surfaced as advisory; not a decision gate in MVP
```

For the full decision tree, see [docs/recommendation-engine.md](recommendation-engine.md).
