"""Qualification fit scorer — weighted score from eligibility results."""

from src.qualification.eligibility import EligibilityResult, RequirementStatus
from src.utils.helpers import clamp
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Mandatory requirements are weighted 2x optional requirements
MANDATORY_WEIGHT = 2
OPTIONAL_WEIGHT = 1


class QualificationScorer:
    """Computes a qualification fit score (0-100) from eligibility results.

    Formula:
        mandatory_score   = (mandatory_met / mandatory_total) * 100
        optional_score    = (optional_met / optional_total) * 100  (100 if no optionals)
        qualification_score = (mandatory_score * 2 + optional_score * 1) / 3

    Partial matches count as 0.5 (not as a full pass).
    """

    def score(self, eligibility_result: EligibilityResult) -> int:
        """Compute the qualification fit score.

        Args:
            eligibility_result: Result from EligibilityChecker.

        Returns:
            Integer score 0-100.
        """
        results = eligibility_result.requirement_results

        mandatory = [r for r in results if r.is_mandatory]
        optional = [r for r in results if not r.is_mandatory]

        mandatory_score = self._compute_category_score(mandatory)
        optional_score = self._compute_category_score(optional) if optional else 100.0

        if not mandatory:
            # No mandatory requirements — score based on optionals only
            final = optional_score
        elif mandatory_score == 0.0:
            # All mandatory requirements failed — hard zero regardless of optionals
            final = 0.0
        else:
            final = (mandatory_score * MANDATORY_WEIGHT + optional_score * OPTIONAL_WEIGHT) / (
                MANDATORY_WEIGHT + OPTIONAL_WEIGHT
            )

        score = int(clamp(final, 0, 100))

        logger.debug(
            "qualification_score_computed",
            mandatory_count=len(mandatory),
            optional_count=len(optional),
            mandatory_score=round(mandatory_score, 1),
            optional_score=round(optional_score, 1),
            final_score=score,
        )

        return score

    def _compute_category_score(self, results: list) -> float:
        """Compute score for a list of requirements (mandatory or optional).

        PASS = 1.0, PARTIAL = 0.5, FAIL = 0.0, NOT_CHECKED = 0.0.
        """
        if not results:
            return 100.0

        total_weight = len(results)
        weighted_sum = 0.0

        for r in results:
            if r.status == RequirementStatus.PASS:
                weighted_sum += 1.0
            elif r.status == RequirementStatus.PARTIAL:
                weighted_sum += 0.5
            # FAIL and NOT_CHECKED contribute 0

        return (weighted_sum / total_weight) * 100

    @staticmethod
    def classify(score: int) -> str:
        """Classify a qualification score as FAIL, MARGINAL, or PASS.

        Args:
            score: Qualification score 0-100.

        Returns:
            "FAIL", "MARGINAL", or "PASS".
        """
        if score >= 80:
            return "PASS"
        elif score >= 60:
            return "MARGINAL"
        else:
            return "FAIL"
