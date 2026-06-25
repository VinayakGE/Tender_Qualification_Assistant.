"""Incumbent risk scorer — estimates likelihood of existing vendor retention."""

import re

from src.utils.helpers import clamp
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Signals that increase incumbent risk with their point values
RISK_SIGNALS: list[tuple[list[str], int]] = [
    (["satisfactory performance", "past performance", "performance in previous"], 25),
    (["existing vendor", "present service provider", "current contractor", "existing contractor"], 20),
    (["annual maintenance", "amc", "renewal", "re-tender", "extended scope"], 20),
    (["continuity of service", "uninterrupted service", "seamless transition"], 15),
    (["contract extended", "extension of contract", "period extended"], 15),
]

# Signals that decrease incumbent risk
RISK_REDUCERS: list[tuple[list[str], int]] = [
    (["cancelled tender", "re-issued", "retender", "poor performance", "terminated contract"], -10),
    (["new implementation", "fresh deployment", "greenfield", "new project"], -15),
    (["new vendors preferred", "encourage new bidders", "msme preferred"], -10),
]

BASE_SCORE = 20
LONG_CONTRACT_MONTHS_THRESHOLD = 36
LONG_CONTRACT_BONUS = 10


class IncumbentRiskScorer:
    """Heuristic scorer for incumbent vendor retention risk.

    Analyzes tender text for language signals that indicate an existing vendor
    is likely to be preferred or retained.
    """

    def score(self, tender_text: str, contract_duration_months: int | None = None) -> int:
        """Compute incumbent risk score from tender text signals.

        Args:
            tender_text: Cleaned tender document text.
            contract_duration_months: Contract duration in months (if known).

        Returns:
            Integer score 0-100. Higher = more incumbent risk.
        """
        text_lower = tender_text.lower()
        risk_score = BASE_SCORE

        # Apply risk-increasing signals
        for keywords, points in RISK_SIGNALS:
            if any(kw in text_lower for kw in keywords):
                risk_score += points
                logger.debug("incumbent_risk_signal", keywords=keywords, points=points)

        # Apply risk-reducing signals
        for keywords, points in RISK_REDUCERS:
            if any(kw in text_lower for kw in keywords):
                risk_score += points  # points are negative
                logger.debug("incumbent_risk_reducer", keywords=keywords, points=points)

        # Long contracts favor incumbents
        if contract_duration_months and contract_duration_months >= LONG_CONTRACT_MONTHS_THRESHOLD:
            risk_score += LONG_CONTRACT_BONUS

        final_score = int(clamp(risk_score, 0, 100))

        logger.debug(
            "incumbent_risk_score",
            raw_score=risk_score,
            final_score=final_score,
            contract_months=contract_duration_months,
        )

        return final_score
