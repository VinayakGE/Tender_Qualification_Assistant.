# Recommendation Engine

## Decision Tree

The recommendation engine applies a strict decision tree. Conditions are evaluated in order; the first matching branch determines the outcome.

```
START
  │
  ├─ Any mandatory requirement status = FAIL?
  │     YES → NO BID  (reason: hard_disqualifier)
  │
  ├─ qualification_score < 60?
  │     YES → NO BID  (reason: score_below_threshold)
  │
  ├─ qualification_score in [60, 79]?
  │   └─ critical evidence gaps present?
  │         YES → REVIEW  (reason: marginal_score_with_gaps)
  │         NO  → REVIEW  (reason: marginal_score)
  │         [Note: score 60-79 always yields REVIEW regardless of gaps]
  │
  └─ qualification_score >= 80?
        └─ critical evidence gaps present?
              YES → REVIEW  (reason: evidence_gaps_block_bid)
              NO  →
                  └─ incumbent_risk >= 70?
                        YES → REVIEW  (reason: high_incumbent_risk)
                        NO  → BID     (reason: all_conditions_met)
```

## Condition Definitions

### Mandatory Requirement Failure

A requirement with `is_mandatory: true` in the requirement schema that has status `FAIL` in the eligibility check. A single mandatory failure is sufficient to trigger NO BID, regardless of qualification score.

This models the reality of Indian government tenders: mandatory pre-qualification criteria are pass/fail gates. A company that does not meet even one of them cannot be considered for evaluation.

### Qualification Score Thresholds

- **< 60 → NO BID**: Score below 60 means the company is failing more mandatory requirements than it is meeting, even accounting for optional requirements. Not viable.
- **60-79 → REVIEW**: Score in this range means the company meets the basic bar but has notable gaps. A human should verify before committing bid resources.
- **80+ → eligible for BID**: Score of 80 or above means the company meets the qualification criteria comprehensively.

### Critical Evidence Gaps

An evidence gap is "critical" if it relates to a mandatory requirement. Specifically:

- The company profile data suggests the requirement is met (e.g., turnover figures are sufficient)
- But there is no documented proof that could be submitted with the bid (e.g., CA-certified audited accounts, completion certificate)

Critical evidence gaps block a BID recommendation because a bid submitted without the required evidence documents will be rejected at evaluation, regardless of the company's actual eligibility.

Evidence gaps are surfaced in the `evidence_gaps` array in the recommendation output.

### Incumbent Risk Threshold

`incumbent_risk >= 70` triggers a downgrade from BID to REVIEW. This is a deliberate conservative threshold. The bid team should make a conscious, informed decision to compete against a strongly entrenched incumbent — the system should not make that decision automatically.

At incumbent_risk 70+, the REVIEW recommendation includes a note explaining the incumbent risk finding so the team can evaluate the competitive strategy.

## Confidence Scoring

Confidence (0.0–1.0) measures how certain the system is about its own recommendation.

```python
base_confidence = 0.5

# Data completeness component (0.0 - 0.25)
completeness = (fields_with_data / total_expected_fields)
completeness_component = completeness * 0.25

# Score margin component (0.0 - 0.15)
# How far is qualification_score from the nearest threshold?
distance_from_threshold = min(
    abs(qualification_score - 60),
    abs(qualification_score - 80)
)
margin_component = min(distance_from_threshold / 20, 1.0) * 0.15

# Requirement coverage component (0.0 - 0.10)
# How many requirements were matched (not just extracted)?
coverage = matched_requirements / extracted_requirements
coverage_component = coverage * 0.10

confidence = base_confidence + completeness_component + margin_component + coverage_component
```

### Confidence Interpretation

| Confidence | Meaning |
|---|---|
| 0.0 – 0.49 | Low confidence — insufficient data for reliable recommendation |
| 0.50 – 0.69 | Moderate confidence — recommendation is directionally correct but should be verified |
| 0.70 – 0.84 | Good confidence — recommendation is reliable under normal circumstances |
| 0.85 – 1.00 | High confidence — strong data completeness and clear score margin |

A confidence below 0.60 is surfaced as a warning to the user: "Low confidence recommendation — verify manually before acting."

## Reasoning Generation

After the decision tree produces a recommendation, the `ExplanationGenerator` calls Claude with `prompts/recommendation.md` to produce a human-readable reasoning paragraph.

The reasoning paragraph must:
1. State the recommendation and qualification score in the first sentence
2. Name the primary bottleneck (if any) specifically
3. List the critical evidence gaps (if any) by name
4. End with a concrete action the bid team should take

Example (REVIEW):

> "Qualification score of 84 passes the 80+ threshold. However, two critical evidence gaps prevent a clean BID recommendation: (1) the tender requires ISO 27001 certification, which is not present in the company profile, and (2) the tender requires documented completion of at least one project valued above ₹5 Cr in the past 5 years — the company's profile shows projects but no completion certificates are on file. Recommend: verify whether these documents exist and can be produced before committing to the bid."

Example (NO BID):

> "Qualification score of 41 falls below the 60-point minimum threshold. The company does not meet the mandatory annual turnover requirement (tender requires ₹50 Cr average over 3 years; company average is ₹28 Cr). This is a hard disqualifier that cannot be resolved without a change in facts. No further bid analysis is warranted."

Example (BID):

> "Qualification score of 91 comfortably passes all eligibility thresholds. All mandatory requirements are met with documented evidence. Incumbent risk score of 48 indicates an open competitive field. Competitive strength score of 74 places the company in a strong position for this contract size and sector. Recommend proceeding to proposal preparation."
