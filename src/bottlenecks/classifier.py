"""Bottleneck classifier — maps qualification failures to taxonomy labels."""

from src.qualification.eligibility import EligibilityResult, RequirementStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Mapping from internal classification to product label
TAXONOMY = {
    "financial_threshold_not_met": "Turnover Requirement Gap",
    "certification_missing": "Certification Gap",
    "experience_threshold_not_met": "Experience Requirement Gap",
    "net_worth_insufficient": "Net Worth Gap",
    "evidence_gap": "Missing Proof",
    "qualification_uncertainty": "Missing Eligibility",
    "competitive_uncertainty": "Competitive Position Unclear",
    "incumbent_risk": "Historical Vendor Dominance",
    "scope_mismatch": "Outside Core Capability",
    "deadline_risk": "Submission Timeline Risk",
    "multiple_disqualifiers": "Multiple Eligibility Gaps",
    "all_clear": None,
}

# Priority order for selecting primary bottleneck (lower index = higher priority)
PRIORITY_ORDER = [
    "financial_threshold_not_met",
    "certification_missing",
    "experience_threshold_not_met",
    "net_worth_insufficient",
    "evidence_gap",
    "qualification_uncertainty",
    "incumbent_risk",
    "competitive_uncertainty",
]


class BottleneckClassifier:
    """Maps qualification results to bottleneck taxonomy labels.

    Used to produce the `primary_bottleneck` field in the recommendation output.
    """

    def classify(
        self,
        eligibility_result: EligibilityResult,
        incumbent_risk_score: int = 0,
    ) -> tuple[str | None, str | None]:
        """Classify the primary bottleneck from eligibility results.

        Args:
            eligibility_result: Result from EligibilityChecker.
            incumbent_risk_score: Incumbent risk score (0-100).

        Returns:
            Tuple of (internal_classification, product_label).
            Both are None if there are no bottlenecks.
        """
        classifications: list[str] = []

        # Check each failed mandatory requirement
        for result in eligibility_result.requirement_results:
            if result.status == RequirementStatus.FAIL:
                if result.category == "turnover":
                    classifications.append("financial_threshold_not_met")
                elif result.category == "certification":
                    classifications.append("certification_missing")
                elif result.category == "experience":
                    classifications.append("experience_threshold_not_met")
                elif result.category == "financial":
                    classifications.append("net_worth_insufficient")
                else:
                    classifications.append("qualification_uncertainty")

        # Evidence gaps on passing requirements
        passing_with_gaps = [
            r
            for r in eligibility_result.requirement_results
            if r.status == RequirementStatus.PASS and not r.evidence_available
        ]
        if passing_with_gaps:
            classifications.append("evidence_gap")

        # Partials indicate uncertainty
        partial_results = [
            r
            for r in eligibility_result.requirement_results
            if r.status == RequirementStatus.PARTIAL
        ]
        if partial_results:
            classifications.append("qualification_uncertainty")

        # High incumbent risk
        if incumbent_risk_score >= 70:
            classifications.append("incumbent_risk")

        # Multiple hard disqualifiers
        hard_disqualifiers = [
            c
            for c in classifications
            if c
            in {
                "financial_threshold_not_met",
                "certification_missing",
                "experience_threshold_not_met",
                "net_worth_insufficient",
            }
        ]
        if len(hard_disqualifiers) > 1:
            classifications.insert(0, "multiple_disqualifiers")

        if not classifications:
            return "all_clear", None

        # Select primary bottleneck by priority
        primary = self._select_primary(classifications)
        product_label = TAXONOMY.get(primary)

        logger.debug(
            "bottleneck_classified",
            all_classifications=list(set(classifications)),
            primary=primary,
            product_label=product_label,
        )

        return primary, product_label

    def _select_primary(self, classifications: list[str]) -> str:
        """Select the highest-priority classification."""
        unique = list(dict.fromkeys(classifications))  # Preserve order, deduplicate

        for priority in PRIORITY_ORDER:
            if priority in unique:
                return priority

        return unique[0] if unique else "qualification_uncertainty"
