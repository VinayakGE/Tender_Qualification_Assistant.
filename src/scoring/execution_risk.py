"""Execution risk scorer — estimates delivery risk based on scope and capacity."""

import re

from src.utils.helpers import clamp
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Keywords that indicate high delivery complexity
COMPLEXITY_KEYWORDS = [
    "integration", "interoperability", "migration", "transformation",
    "multi-site", "multiple locations", "24x7", "24/7", "round the clock",
    "sla", "service level", "penalty clause", "liquidated damages",
    "performance bond", "bank guarantee", "mobilization",
    "commissioning", "testing and commissioning", "factory acceptance",
    "site acceptance", "parallel run",
]

MAX_COMPLEXITY_SCORE = 30
MAX_TIMELINE_SCORE = 20
MAX_CAPACITY_SCORE = 25
MAX_EXPERIENCE_GAP_SCORE = 25


class ExecutionRiskScorer:
    """Estimates execution/delivery risk for a tender.

    Components:
    - Timeline risk: short duration → high risk
    - Scope complexity: complexity keyword count
    - Capacity risk: company headcount vs estimated team size
    - Experience gap: proportion of requirements outside company's experience
    """

    def score(
        self,
        tender_text: str,
        company_profile: dict,
        contract_duration_months: int | None,
        requirements_count: int = 0,
        qualification_score: int = 80,
    ) -> int:
        """Compute execution risk score.

        Args:
            tender_text: Cleaned tender text.
            company_profile: Company profile dict.
            contract_duration_months: Contract duration in months.
            requirements_count: Number of extracted requirements.
            qualification_score: Qualification fit score (used to proxy experience gaps).

        Returns:
            Integer score 0-100.
        """
        timeline_risk = self._timeline_risk(contract_duration_months)
        scope_complexity = self._scope_complexity(tender_text)
        capacity_risk = self._capacity_risk(company_profile, requirements_count)
        experience_gap = self._experience_gap(qualification_score)

        raw_score = timeline_risk + scope_complexity + capacity_risk + experience_gap
        final_score = int(clamp(raw_score, 0, 100))

        logger.debug(
            "execution_risk_score",
            timeline_risk=round(timeline_risk, 1),
            scope_complexity=round(scope_complexity, 1),
            capacity_risk=round(capacity_risk, 1),
            experience_gap=round(experience_gap, 1),
            final_score=final_score,
        )

        return final_score

    def _timeline_risk(self, duration_months: int | None) -> float:
        """Short timelines increase risk. Max contribution: 20."""
        if duration_months is None:
            return 10.0  # Default if unknown
        # Less than 6 months → high risk; more than 24 months → low risk
        if duration_months <= 6:
            return 20.0
        elif duration_months <= 12:
            return 15.0
        elif duration_months <= 24:
            return 8.0
        else:
            return 3.0

    def _scope_complexity(self, text: str) -> float:
        """Count complexity keywords. Max contribution: 30."""
        text_lower = text.lower()
        count = sum(1 for kw in COMPLEXITY_KEYWORDS if kw in text_lower)
        # Each keyword adds ~3 points, capped at 30
        return clamp(count * 3.0, 0, MAX_COMPLEXITY_SCORE)

    def _capacity_risk(self, company_profile: dict, requirements_count: int) -> float:
        """Estimate if company has enough staff for this scope. Max: 25."""
        employees = company_profile.get("employees")
        if employees is None:
            return 12.5  # Default

        # Rough estimate: 2 staff per requirement for a complex tender
        estimated_team = max(5, requirements_count * 2)
        ratio = employees / estimated_team

        if ratio >= 5:
            return 0.0  # Very well-staffed
        elif ratio >= 2:
            return 10.0
        elif ratio >= 1:
            return 18.0
        else:
            return 25.0  # Understaffed

    def _experience_gap(self, qualification_score: int) -> float:
        """Proxy for experience gaps using qualification score. Max: 25."""
        # Lower qualification score → more unfamiliar requirements → higher execution risk
        gap_factor = max(0, (80 - qualification_score)) / 80
        return gap_factor * MAX_EXPERIENCE_GAP_SCORE
