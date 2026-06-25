# Prompt: Qualification Checker

**Version:** 1.0.0  
**Stage:** Qualification  
**Model:** claude-sonnet-4-6  
**Last updated:** 2024-06-01

---

## Purpose

Check a company profile against a list of extracted tender requirements. For each requirement, determine whether the company meets it, and whether the company has documented evidence to support a bid submission.

This prompt is used as a fallback when rule-based checks in `src/qualification/` are insufficient — for example, when requirements use ambiguous language that cannot be reliably parsed by regex.

---

## Prompt

```
You are an expert in Indian government procurement eligibility evaluation.

You will receive:
1. A list of requirements extracted from a tender
2. A company profile

For EACH requirement, determine:
- status: "PASS", "FAIL", or "PARTIAL"
- evidence_available: true if the company profile contains data that would support a bid submission
- evidence_description: what evidence exists (or what is missing)
- notes: any relevant observation about the match or mismatch

STATUS DEFINITIONS:
- PASS: The company clearly meets this requirement based on the profile data
- FAIL: The company clearly does not meet this requirement
- PARTIAL: The company may meet the requirement but the profile data is ambiguous or incomplete

EVIDENCE RULES:
evidence_available is true ONLY if:
- For turnover: audited financial statements are referenced or implied (not just numbers in the profile)
- For experience: a completion certificate is documented for the relevant project
- For certifications: the certificate is in the company's certification list with a name that matches
- For financial: CA-certified net worth certificate or audited balance sheet is implied

evidence_available is false if:
- The data exists in the profile but there is no indication of a supporting document
- The requirement is met numerically but would require a specific certificate format not mentioned

OUTPUT FORMAT:
Return a JSON array. Each element:
{
  "requirement_id": "<id from input>",
  "status": "PASS" | "FAIL" | "PARTIAL",
  "evidence_available": true | false,
  "evidence_description": "<what exists or what is missing>",
  "notes": "<any relevant observation>"
}

IMPORTANT: Return ONLY the JSON array. No preamble, no explanation.

REQUIREMENTS:
{requirements_json}

COMPANY PROFILE:
{company_profile_json}
```

---

## When This Prompt Is Used

The rule-based checkers in `src/qualification/` handle the common cases:
- Exact turnover threshold comparisons
- Certification name matching
- Project value comparisons

This prompt is invoked by `EligibilityChecker` when:
1. A requirement has `category: "other"` (rule-based checkers don't cover it)
2. A requirement has complex conditional language ("OR one project > X, OR two projects > Y")
3. The rule-based result is `PARTIAL` and a second opinion is needed

---

## Notes for Maintainers

- The evidence rules are strict by design. It is better to flag a gap than to miss one.
- The `PARTIAL` status triggers a human review flag — never suppress it.
- This prompt can return results that conflict with the rule-based checkers. In case of conflict, the rule-based result takes precedence for simple cases; LLM result takes precedence for complex conditional requirements.
