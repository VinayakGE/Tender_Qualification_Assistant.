"""Competitive strength scorer."""

from src.utils.helpers import clamp
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CompetitivenessScorer:
    """Estimates the company's competitive position for a given tender.

    Score components:
    - Size factor (max 60): company turnover relative to contract value
    - Experience match (max 25): sector-specific experience
    - Capacity factor (max 15): staffing relative to estimated team size
    """

    def score(
        self,
        company_profile: dict,
        contract_value_inr: float | None,
        tender_sector: str | None,
        requirements_count: int = 0,
    ) -> int:
        """Compute competitive strength score.

        Args:
            company_profile: Company profile dict.
            contract_value_inr: Contract value in INR (raw rupees, not Crores).
            tender_sector: Tender sector/type for experience matching.
            requirements_count: Number of extracted requirements (complexity proxy).

        Returns:
            Integer score 0-100.
        """
        size_factor = self._size_factor(company_profile, contract_value_inr)
        experience_match = self._experience_match(company_profile, tender_sector)
        capacity_factor = self._capacity_factor(company_profile, requirements_count)

        raw_score = size_factor + experience_match + capacity_factor

        score = int(clamp(raw_score, 0, 100))

        logger.debug(
            "competitiveness_score",
            size_factor=round(size_factor, 1),
            experience_match=round(experience_match, 1),
            capacity_factor=round(capacity_factor, 1),
            final_score=score,
        )

        return score

    def _size_factor(self, company_profile: dict, contract_value_inr: float | None) -> float:
        """Company size vs contract size factor (max 60)."""
        turnovers = company_profile.get("annual_turnover_inr_crores", [])
        if not turnovers or not contract_value_inr or contract_value_inr <= 0:
            return 30.0  # Default mid-range if no data

        avg_turnover_inr = (sum(turnovers) / len(turnovers)) * 1e7  # Convert Crores to INR

        ratio = avg_turnover_inr / contract_value_inr
        # Log scale: ratio of 1.0 → 30 points, 3.0+ → 60 points
        factor = min(ratio / 3.0, 1.0) * 60
        return clamp(factor, 0, 60)

    def _experience_match(self, company_profile: dict, tender_sector: str | None) -> float:
        """Sector experience matching score (max 25)."""
        if not tender_sector:
            return 12.5  # Default if sector unknown

        projects = company_profile.get("completed_projects", [])
        priority_sectors = [s.lower() for s in company_profile.get("priority_sectors", [])]
        tender_sector_lower = tender_sector.lower()

        # Count projects in the matching sector
        matching = sum(
            1
            for p in projects
            if tender_sector_lower in (p.get("sector") or "").lower()
            or (p.get("sector") or "").lower() in tender_sector_lower
        )

        # Bonus if tender sector is in priority sectors
        priority_bonus = (
            5.0
            if any(tender_sector_lower in s or s in tender_sector_lower for s in priority_sectors)
            else 0.0
        )

        # Scale: 0 matches → 0, 1 match → 10, 2+ → 15, 3+ → 20, priority bonus → up to 25
        base = min(matching * 7, 20)
        return clamp(base + priority_bonus, 0, 25)

    def _capacity_factor(self, company_profile: dict, requirements_count: int) -> float:
        """Staff capacity factor (max 15)."""
        employees = company_profile.get("employees")
        if employees is None:
            return 7.5  # Default

        # Rough heuristic: complex tenders need more staff
        estimated_team = max(5, requirements_count * 2)
        ratio = employees / estimated_team
        return clamp(min(ratio / 10, 1.0) * 15, 0, 15)
