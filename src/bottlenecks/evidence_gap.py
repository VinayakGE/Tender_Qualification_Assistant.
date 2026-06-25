"""Evidence gap detector — identifies requirements lacking documented proof."""

from src.qualification.eligibility import EligibilityResult, RequirementStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Evidence gap descriptions by requirement category
GAP_DESCRIPTIONS = {
    "turnover": "CA-certified audited accounts for {} years not documented in company profile",
    "experience": "Completion certificate for qualifying project not on file",
    "certification": "Certificate document for {} not referenced in company profile",
    "financial": "CA-certified net worth certificate not documented in company profile",
    "technical": "Technical capability documentation not available",
    "other": "Supporting documentation not available",
}


class EvidenceGapDetector:
    """Identifies evidence gaps — requirements met numerically but lacking proof documents.

    A gap is defined as: requirement status is PASS but evidence_available is False.
    These are critical because a bid submission will be rejected without the documents,
    regardless of the company's actual eligibility.
    """

    def detect(self, eligibility_result: EligibilityResult) -> list[str]:
        """Detect all evidence gaps in the eligibility result.

        Args:
            eligibility_result: Result from EligibilityChecker.

        Returns:
            List of human-readable evidence gap descriptions.
        """
        gaps: list[str] = []

        for result in eligibility_result.requirement_results:
            if result.status in (RequirementStatus.PASS, RequirementStatus.PARTIAL):
                if not result.evidence_available:
                    gap_desc = self._describe_gap(result)
                    gaps.append(gap_desc)
                    logger.debug(
                        "evidence_gap_detected",
                        requirement_id=result.requirement_id,
                        category=result.category,
                        gap=gap_desc,
                    )

        logger.info(
            "evidence_gaps_detected",
            total_gaps=len(gaps),
            mandatory_gaps=sum(
                1 for r in eligibility_result.requirement_results
                if not r.evidence_available and r.is_mandatory
            ),
        )

        return gaps

    def detect_critical(self, eligibility_result: EligibilityResult) -> list[str]:
        """Return only gaps for mandatory requirements.

        Critical gaps are those on mandatory requirements — they block a BID recommendation.

        Args:
            eligibility_result: Result from EligibilityChecker.

        Returns:
            List of gap descriptions for mandatory requirements only.
        """
        critical: list[str] = []

        for result in eligibility_result.requirement_results:
            if result.is_mandatory and not result.evidence_available:
                if result.status in (RequirementStatus.PASS, RequirementStatus.PARTIAL):
                    critical.append(self._describe_gap(result))

        return critical

    def _describe_gap(self, result) -> str:
        """Produce a human-readable gap description for a requirement result."""
        base = result.evidence_description or result.description

        # If the evidence description already explains the gap, use it directly
        if "not" in base.lower() or "missing" in base.lower() or "no " in base.lower():
            return base

        # Otherwise, construct a standard gap description
        template = GAP_DESCRIPTIONS.get(result.category, GAP_DESCRIPTIONS["other"])
        try:
            return template.format(result.description[:60])
        except (IndexError, KeyError):
            return f"{result.description[:60]} — supporting documentation not available"
