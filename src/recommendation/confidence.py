"""Confidence score estimator for recommendation reliability."""

from src.qualification.eligibility import EligibilityResult, RequirementStatus
from src.utils.helpers import clamp
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConfidenceEstimator:
    """Estimates confidence in a recommendation (0.0 to 1.0).

    Confidence is a measure of data completeness and score margin:
    - Higher when all requirements have definitive PASS/FAIL (not PARTIAL)
    - Higher when the qualification score is far from both thresholds (60 and 80)
    - Higher when evidence is available for passing requirements
    - Lower when many requirements could not be automatically checked

    Formula:
        base = 0.50
        + completeness_component (0 - 0.25): % requirements not PARTIAL
        + margin_component (0 - 0.15): distance from nearest threshold / 20
        + evidence_component (0 - 0.10): % of passing reqs with evidence
        = max 1.0
    """

    def estimate(
        self,
        eligibility_result: EligibilityResult,
        qualification_score: int,
        competitive_strength: int = 50,
    ) -> float:
        """Estimate confidence in the recommendation.

        Args:
            eligibility_result: Result from EligibilityChecker.
            qualification_score: Qualification fit score (0-100).
            competitive_strength: Competitive strength score for adjustment.

        Returns:
            Confidence score 0.0-1.0.
        """
        results = eligibility_result.requirement_results

        if not results:
            return 0.50  # No data → base confidence only

        # Component 1: Data completeness (0 - 0.25)
        # PARTIAL statuses indicate uncertainty
        definitive = sum(
            1 for r in results
            if r.status in (RequirementStatus.PASS, RequirementStatus.FAIL)
        )
        completeness = definitive / len(results)
        completeness_component = completeness * 0.25

        # Component 2: Score margin from nearest threshold (0 - 0.15)
        distance = min(
            abs(qualification_score - 60),
            abs(qualification_score - 80),
        )
        margin_component = min(distance / 20.0, 1.0) * 0.15

        # Component 3: Evidence availability on passing requirements (0 - 0.10)
        passing = [r for r in results if r.status == RequirementStatus.PASS]
        if passing:
            evidence_ratio = sum(1 for r in passing if r.evidence_available) / len(passing)
        else:
            evidence_ratio = 0.5
        evidence_component = evidence_ratio * 0.10

        base = 0.50
        confidence = base + completeness_component + margin_component + evidence_component
        final = round(clamp(confidence, 0.0, 1.0), 2)

        logger.debug(
            "confidence_estimated",
            base=base,
            completeness_component=round(completeness_component, 3),
            margin_component=round(margin_component, 3),
            evidence_component=round(evidence_component, 3),
            final_confidence=final,
        )

        return final
