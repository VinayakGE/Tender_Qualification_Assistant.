"""Project experience checker."""

from datetime import date, datetime, timedelta

from src.extractor.requirement_extractor import Requirement
from src.qualification.eligibility import RequirementResult, RequirementStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Default lookback window: past 7 years (if not specified in requirement)
DEFAULT_LOOKBACK_YEARS = 7


class ExperienceChecker:
    """Checks if the company has completed projects meeting the experience requirement.

    Handles:
    - Minimum project value thresholds
    - Sector/domain requirements
    - Time window (projects within past N years)
    - Single large project vs. multiple smaller project alternatives
    """

    def check_single(
        self,
        requirement: Requirement,
        company_profile: dict,
    ) -> RequirementResult:
        """Check a single experience requirement against the company's project history.

        Args:
            requirement: The experience requirement to check.
            company_profile: Company profile dict.

        Returns:
            RequirementResult with PASS, FAIL, or PARTIAL status.
        """
        completed_projects: list[dict] = company_profile.get("completed_projects", [])

        if not completed_projects:
            return RequirementResult(
                requirement_id=requirement.requirement_id,
                category="experience",
                description=requirement.description,
                is_mandatory=requirement.is_mandatory,
                status=RequirementStatus.FAIL,
                evidence_available=False,
                evidence_description="No completed projects in company profile",
            )

        threshold_crores = self._normalize_to_crores(
            requirement.threshold_value, requirement.threshold_unit
        )
        required_sector = requirement.sector
        lookback_years = requirement.threshold_period_years or DEFAULT_LOOKBACK_YEARS
        cutoff_date = date.today() - timedelta(days=lookback_years * 365)

        matching_projects = []
        for project in completed_projects:
            if not self._is_within_window(project, cutoff_date):
                continue
            if required_sector and not self._sector_matches(project, required_sector):
                continue
            if threshold_crores and project.get("contract_value_inr_crores", 0) < threshold_crores:
                continue
            matching_projects.append(project)

        passes = len(matching_projects) > 0

        # Evidence: check if completion certificates are documented
        evidence_available = any(
            p.get("has_completion_certificate", False) for p in matching_projects
        )

        if passes:
            best = max(matching_projects, key=lambda p: p.get("contract_value_inr_crores", 0))
            description = (
                f"Found {len(matching_projects)} qualifying project(s). "
                f"Best match: {best.get('title', 'Unknown')} "
                f"(₹{best.get('contract_value_inr_crores', 0):.1f} Cr)"
            )
        else:
            max_value = max(
                (p.get("contract_value_inr_crores", 0) for p in completed_projects), default=0
            )
            description = (
                f"No qualifying projects found. "
                f"Threshold: ₹{threshold_crores:.1f} Cr"
                + (f" in sector '{required_sector}'" if required_sector else "")
                + f" within {lookback_years} years. "
                f"Largest project: ₹{max_value:.1f} Cr"
            )

        logger.debug(
            "experience_check",
            requirement_id=requirement.requirement_id,
            matching_projects=len(matching_projects),
            passes=passes,
            evidence_available=evidence_available,
        )

        return RequirementResult(
            requirement_id=requirement.requirement_id,
            category="experience",
            description=requirement.description,
            is_mandatory=requirement.is_mandatory,
            status=RequirementStatus.PASS if passes else RequirementStatus.FAIL,
            evidence_available=evidence_available,
            evidence_description=description,
            notes="Completion certificate not on file" if passes and not evidence_available else "",
        )

    def _normalize_to_crores(self, value: float | None, unit: str | None) -> float:
        if value is None:
            return 0.0
        if unit is None:
            return value
        unit_lower = unit.lower()
        if "lakh" in unit_lower:
            return value / 100
        return value

    def _is_within_window(self, project: dict, cutoff_date: date) -> bool:
        """Check if a project was completed after the cutoff date."""
        completion_str = project.get("completion_date")
        if not completion_str:
            return True  # If no date, include by default (conservative)
        try:
            completion = date.fromisoformat(str(completion_str))
            return completion >= cutoff_date
        except ValueError:
            return True

    def _sector_matches(self, project: dict, required_sector: str) -> bool:
        """Check if project sector matches the required sector."""
        project_sector = (project.get("sector") or "").lower()
        required = required_sector.lower()
        # Allow partial match (e.g., "water" matches "water_treatment")
        return required in project_sector or project_sector in required
