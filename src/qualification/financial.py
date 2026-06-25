"""Financial threshold checker (net worth, working capital)."""

from src.extractor.requirement_extractor import Requirement
from src.qualification.eligibility import RequirementResult, RequirementStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)

FINANCIAL_KEYWORDS = {
    "net_worth": ["net worth", "networth", "net-worth"],
    "working_capital": ["working capital", "current ratio", "liquidity"],
    "solvency": ["solvency", "debt", "leverage", "gearing"],
}


class FinancialChecker:
    """Checks financial requirements against company profile.

    Covers net worth, working capital, and solvency thresholds.
    """

    def check_single(
        self,
        requirement: Requirement,
        company_profile: dict,
    ) -> RequirementResult:
        """Check a single financial requirement.

        Args:
            requirement: The financial requirement to check.
            company_profile: Company profile dict.

        Returns:
            RequirementResult with PASS, FAIL, or PARTIAL status.
        """
        description_lower = requirement.description.lower()

        # Determine which financial metric this requirement refers to
        if any(kw in description_lower for kw in FINANCIAL_KEYWORDS["net_worth"]):
            return self._check_net_worth(requirement, company_profile)
        elif any(kw in description_lower for kw in FINANCIAL_KEYWORDS["working_capital"]):
            return self._check_working_capital(requirement, company_profile)
        else:
            # Generic financial check — use net worth as proxy
            return self._check_net_worth(requirement, company_profile)

    def _check_net_worth(
        self,
        requirement: Requirement,
        company_profile: dict,
    ) -> RequirementResult:
        """Check net worth threshold."""
        net_worth = company_profile.get("financial_net_worth_inr_crores")

        if net_worth is None:
            return RequirementResult(
                requirement_id=requirement.requirement_id,
                category="financial",
                description=requirement.description,
                is_mandatory=requirement.is_mandatory,
                status=RequirementStatus.PARTIAL,
                evidence_available=False,
                evidence_description="Net worth not provided in company profile",
            )

        threshold = self._normalize_to_crores(
            requirement.threshold_value, requirement.threshold_unit
        )

        if threshold is None:
            return RequirementResult(
                requirement_id=requirement.requirement_id,
                category="financial",
                description=requirement.description,
                is_mandatory=requirement.is_mandatory,
                status=RequirementStatus.PARTIAL,
                evidence_available=True,
                evidence_description=f"No numeric threshold extracted. Company net worth: ₹{net_worth:.1f} Cr",
            )

        passes = net_worth >= threshold
        description = f"Net worth: ₹{net_worth:.1f} Cr vs threshold ₹{threshold:.1f} Cr"

        logger.debug(
            "financial_net_worth_check",
            requirement_id=requirement.requirement_id,
            net_worth=net_worth,
            threshold=threshold,
            passes=passes,
        )

        return RequirementResult(
            requirement_id=requirement.requirement_id,
            category="financial",
            description=requirement.description,
            is_mandatory=requirement.is_mandatory,
            status=RequirementStatus.PASS if passes else RequirementStatus.FAIL,
            evidence_available=True,
            evidence_description=description,
            notes="" if passes else f"Gap: ₹{threshold - net_worth:.1f} Cr short",
        )

    def _check_working_capital(
        self,
        requirement: Requirement,
        company_profile: dict,
    ) -> RequirementResult:
        """Check working capital threshold."""
        working_capital = company_profile.get("working_capital_inr_crores")

        if working_capital is None:
            return RequirementResult(
                requirement_id=requirement.requirement_id,
                category="financial",
                description=requirement.description,
                is_mandatory=requirement.is_mandatory,
                status=RequirementStatus.PARTIAL,
                evidence_available=False,
                evidence_description="Working capital not provided in company profile",
            )

        threshold = self._normalize_to_crores(
            requirement.threshold_value, requirement.threshold_unit
        )

        if threshold is None:
            return RequirementResult(
                requirement_id=requirement.requirement_id,
                category="financial",
                description=requirement.description,
                is_mandatory=requirement.is_mandatory,
                status=RequirementStatus.PARTIAL,
                evidence_available=True,
                evidence_description=f"No numeric threshold extracted. Working capital: ₹{working_capital:.1f} Cr",
            )

        passes = working_capital >= threshold
        return RequirementResult(
            requirement_id=requirement.requirement_id,
            category="financial",
            description=requirement.description,
            is_mandatory=requirement.is_mandatory,
            status=RequirementStatus.PASS if passes else RequirementStatus.FAIL,
            evidence_available=True,
            evidence_description=f"Working capital: ₹{working_capital:.1f} Cr vs threshold ₹{threshold:.1f} Cr",
        )

    def _normalize_to_crores(self, value: float | None, unit: str | None) -> float | None:
        if value is None:
            return None
        if unit is None:
            return value
        unit_lower = unit.lower()
        if "lakh" in unit_lower:
            return value / 100
        return value
