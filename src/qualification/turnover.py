"""Turnover threshold checker."""

from src.extractor.requirement_extractor import Requirement
from src.qualification.eligibility import RequirementResult, RequirementStatus
from src.utils.helpers import safe_avg
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TurnoverChecker:
    """Checks if a company's annual turnover meets the tender's threshold.

    Handles both "annual turnover >= X" and "average annual turnover over N years >= X" patterns.
    """

    def check_single(
        self,
        requirement: Requirement,
        company_profile: dict,
    ) -> RequirementResult:
        """Check a single turnover requirement against the company profile.

        Args:
            requirement: The turnover requirement to check.
            company_profile: Company profile dict.

        Returns:
            RequirementResult with PASS, FAIL, or PARTIAL status.
        """
        turnover_history: list[float] = company_profile.get("annual_turnover_inr_crores", [])

        if not turnover_history:
            return RequirementResult(
                requirement_id=requirement.requirement_id,
                category="turnover",
                description=requirement.description,
                is_mandatory=requirement.is_mandatory,
                status=RequirementStatus.PARTIAL,
                evidence_available=False,
                evidence_description="No turnover data in company profile",
            )

        threshold = requirement.threshold_value
        if threshold is None:
            return RequirementResult(
                requirement_id=requirement.requirement_id,
                category="turnover",
                description=requirement.description,
                is_mandatory=requirement.is_mandatory,
                status=RequirementStatus.PARTIAL,
                evidence_available=False,
                evidence_description="No numeric threshold extracted from requirement",
            )

        # Normalize threshold to INR Crores
        threshold_inr_crores = self._normalize_to_crores(threshold, requirement.threshold_unit)

        # Determine lookback period
        period = requirement.threshold_period_years or 1
        relevant_turnovers = turnover_history[:period]

        if len(relevant_turnovers) < period:
            logger.warning(
                "turnover_insufficient_history",
                required_years=period,
                available_years=len(relevant_turnovers),
            )

        if period > 1:
            # Average annual turnover over N years
            company_value = safe_avg(relevant_turnovers)
            check_description = f"Average annual turnover over {len(relevant_turnovers)} years: ₹{company_value:.1f} Cr vs threshold ₹{threshold_inr_crores:.1f} Cr"
        else:
            # Single year turnover (use most recent)
            company_value = relevant_turnovers[0]
            check_description = f"Annual turnover (most recent): ₹{company_value:.1f} Cr vs threshold ₹{threshold_inr_crores:.1f} Cr"

        passes = company_value >= threshold_inr_crores

        # Evidence: audited accounts are implied by the profile data, but not guaranteed
        evidence_available = len(turnover_history) >= period

        logger.debug(
            "turnover_check",
            requirement_id=requirement.requirement_id,
            company_value=company_value,
            threshold=threshold_inr_crores,
            passes=passes,
        )

        return RequirementResult(
            requirement_id=requirement.requirement_id,
            category="turnover",
            description=requirement.description,
            is_mandatory=requirement.is_mandatory,
            status=RequirementStatus.PASS if passes else RequirementStatus.FAIL,
            evidence_available=evidence_available,
            evidence_description=check_description,
            notes=f"Gap: ₹{threshold_inr_crores - company_value:.1f} Cr short" if not passes else "",
        )

    def _normalize_to_crores(self, value: float, unit: str | None) -> float:
        """Normalize a value to INR Crores based on unit."""
        if unit is None:
            return value  # Assume already in Crores
        unit_lower = unit.lower()
        if "lakh" in unit_lower or "l" == unit_lower:
            return value / 100
        if "crore" in unit_lower or "cr" in unit_lower:
            return value
        if "inr" in unit_lower and "crore" in unit_lower:
            return value
        # Default: assume Crores
        return value
