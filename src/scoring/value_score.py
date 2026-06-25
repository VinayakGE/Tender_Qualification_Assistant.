"""Value score — composite of contract value, strategic fit, and win probability."""

import math

from src.utils.helpers import clamp
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Score component weights (must sum to 100)
CONTRACT_VALUE_WEIGHT = 35
STRATEGIC_FIT_WEIGHT = 30
WIN_PROBABILITY_WEIGHT = 35

# Contract value normalization range (in INR)
MIN_CONTRACT_INR = 100_000  # ₹1 Lakh
MAX_CONTRACT_INR = 1_000_000_000  # ₹100 Crore


class ValueScorer:
    """Computes a composite value score for a tender opportunity.

    Components:
    - Contract value score (35%): logarithmic scale of contract size
    - Strategic fit score (30%): alignment with company's priority sectors
    - Win probability score (35%): derived from qualification, competitiveness, incumbent risk
    """

    def score(
        self,
        company_profile: dict,
        contract_value_inr: float | None,
        tender_sector: str | None,
        qualification_score: int,
        competitive_strength: int,
        incumbent_risk: int,
    ) -> int:
        """Compute value score.

        Args:
            company_profile: Company profile dict.
            contract_value_inr: Contract value in INR (raw rupees).
            tender_sector: Tender sector string.
            qualification_score: Qualification fit score (0-100).
            competitive_strength: Competitive strength score (0-100).
            incumbent_risk: Incumbent risk score (0-100, higher = more risk).

        Returns:
            Integer value score 0-100.
        """
        contract_component = self._contract_value_component(contract_value_inr)
        strategic_component = self._strategic_fit_component(company_profile, tender_sector)
        win_component = self._win_probability_component(
            qualification_score, competitive_strength, incumbent_risk
        )

        raw_score = (
            contract_component * CONTRACT_VALUE_WEIGHT / 100
            + strategic_component * STRATEGIC_FIT_WEIGHT / 100
            + win_component * WIN_PROBABILITY_WEIGHT / 100
        )

        final_score = int(clamp(raw_score, 0, 100))

        logger.debug(
            "value_score",
            contract_component=round(contract_component, 1),
            strategic_component=round(strategic_component, 1),
            win_component=round(win_component, 1),
            final_score=final_score,
        )

        return final_score

    def _contract_value_component(self, contract_value_inr: float | None) -> float:
        """Map contract value to 0-100 using logarithmic scale."""
        if not contract_value_inr or contract_value_inr <= 0:
            return 50.0  # Default mid-range if unknown

        # Log scale: MIN → 0, MAX → 100
        log_min = math.log10(MIN_CONTRACT_INR)
        log_max = math.log10(MAX_CONTRACT_INR)
        log_val = math.log10(max(contract_value_inr, MIN_CONTRACT_INR))

        normalized = (log_val - log_min) / (log_max - log_min)
        return clamp(normalized * 100, 0, 100)

    def _strategic_fit_component(self, company_profile: dict, tender_sector: str | None) -> float:
        """Score strategic fit based on priority sectors."""
        if not tender_sector:
            return 50.0

        priority_sectors = [s.lower() for s in company_profile.get("priority_sectors", [])]
        tender_lower = tender_sector.lower()

        # Perfect match → 100, related → 60, no match → 20
        if any(tender_lower in s or s in tender_lower for s in priority_sectors):
            return 100.0

        # Check completed project sectors as a proxy for capability
        project_sectors = [
            (p.get("sector") or "").lower() for p in company_profile.get("completed_projects", [])
        ]
        if any(tender_lower in s or s in tender_lower for s in project_sectors):
            return 60.0

        return 20.0

    def _win_probability_component(
        self,
        qualification_score: int,
        competitive_strength: int,
        incumbent_risk: int,
    ) -> float:
        """Estimate win probability from the three core scores."""
        # qualification and competitiveness drive win probability up
        # incumbent risk drives it down
        win_prob = (
            (qualification_score * 0.4)
            + (competitive_strength * 0.4)
            + ((100 - incumbent_risk) * 0.2)
        )
        return clamp(win_prob, 0, 100)
