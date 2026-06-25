"""Reasoning builder — constructs structured reasoning strings from bottleneck data."""

from src.qualification.eligibility import EligibilityResult, RequirementStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ReasoningBuilder:
    """Constructs human-readable reasoning text from bottleneck and score data.

    Used to produce the `reasoning` field before the LLM explanation is generated.
    This provides a fallback reasoning if the LLM call fails, and seeds the LLM prompt.
    """

    def build(
        self,
        eligibility_result: EligibilityResult,
        qualification_score: int,
        incumbent_risk_score: int,
        primary_bottleneck: str | None,
        evidence_gaps: list[str],
        recommendation: str,
    ) -> str:
        """Build a structured reasoning string.

        Args:
            eligibility_result: Result from EligibilityChecker.
            qualification_score: Qualification fit score (0-100).
            incumbent_risk_score: Incumbent risk score (0-100).
            primary_bottleneck: Primary bottleneck product label.
            evidence_gaps: List of evidence gap descriptions.
            recommendation: Final recommendation (BID/REVIEW/NO_BID).

        Returns:
            Multi-sentence reasoning string.
        """
        parts: list[str] = []

        # Opening: recommendation + score
        score_classification = self._classify_score(qualification_score)
        parts.append(
            f"Qualification score of {qualification_score} ({score_classification}). "
            f"Recommendation: {recommendation}."
        )

        # Mandatory failures
        failed_mandatory = [
            r
            for r in eligibility_result.requirement_results
            if r.is_mandatory and r.status == RequirementStatus.FAIL
        ]
        if failed_mandatory:
            for r in failed_mandatory[:3]:  # Cap at 3 to keep text concise
                parts.append(
                    f"Mandatory requirement failed: {r.description}. {r.evidence_description}"
                )

        # Evidence gaps
        if evidence_gaps:
            gap_list = "; ".join(evidence_gaps[:3])
            parts.append(f"Evidence gaps: {gap_list}.")

        # Incumbent risk
        if incumbent_risk_score >= 70:
            parts.append(
                f"High incumbent risk ({incumbent_risk_score}/100) — "
                "existing vendor shows strong retention signals in tender language."
            )

        # Primary bottleneck
        if primary_bottleneck and recommendation != "BID":
            parts.append(f"Primary bottleneck: {primary_bottleneck}.")

        return " ".join(parts)

    def _classify_score(self, score: int) -> str:
        if score >= 80:
            return "PASS"
        elif score >= 60:
            return "MARGINAL"
        else:
            return "FAIL"
