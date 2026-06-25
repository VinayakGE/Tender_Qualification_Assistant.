"""Outcome tracker — records actual bid outcomes against recommendations."""

import json
from pathlib import Path

from src.utils.config import get_config
from src.utils.helpers import ensure_dir, generate_id, now_iso, save_json, load_json
from src.utils.logger import get_logger

logger = get_logger(__name__)

OUTCOMES_FILE_NAME = "outcomes-ledger.json"


class OutcomeTracker:
    """Records and retrieves actual bid outcomes.

    Outcomes are stored in data/outcomes/outcomes-ledger.json.
    Each outcome links back to a recommendation_id, enabling accuracy measurement.
    """

    def __init__(self) -> None:
        self.config = get_config()
        ensure_dir(self.config.OUTCOMES_DIR)
        self.outcomes_path = self.config.OUTCOMES_DIR / OUTCOMES_FILE_NAME
        self._initialize_if_empty()

    def record(
        self,
        recommendation_id: str,
        tender_id: str,
        company_id: str,
        bid_submitted: bool,
        bid_won: bool | None = None,
        contract_value_inr: float | None = None,
        system_recommendation: str | None = None,
        human_decision: str | None = None,
        disqualified_at_evaluation: bool | None = None,
        loss_reason: str | None = None,
        notes: str | None = None,
    ) -> dict:
        """Record an actual bid outcome.

        Args:
            recommendation_id: The recommendation this outcome corresponds to.
            tender_id: The tender ID.
            company_id: The company ID.
            bid_submitted: Whether a bid was submitted.
            bid_won: Whether the bid was won (None if result not yet known).
            contract_value_inr: Contract value if won.
            system_recommendation: What the system recommended (BID/REVIEW/NO_BID).
            human_decision: What the team actually decided.
            disqualified_at_evaluation: Whether the bid was disqualified during evaluation.
            loss_reason: Why the bid was lost (if applicable).
            notes: Free-text notes.

        Returns:
            The outcome dict that was saved.
        """
        outcome = {
            "outcome_id": generate_id("out"),
            "recommendation_id": recommendation_id,
            "tender_id": tender_id,
            "company_id": company_id,
            "system_recommendation": system_recommendation,
            "human_decision": human_decision,
            "bid_submitted": bid_submitted,
            "bid_won": bid_won,
            "contract_value_inr": contract_value_inr,
            "disqualified_at_evaluation": disqualified_at_evaluation,
            "loss_reason": loss_reason,
            "notes": notes,
            "recorded_at": now_iso(),
        }

        # Append to outcomes ledger
        existing = self._load()
        existing.append(outcome)
        save_json(existing, self.outcomes_path)

        logger.info(
            "outcome_recorded",
            outcome_id=outcome["outcome_id"],
            recommendation_id=recommendation_id,
            bid_submitted=bid_submitted,
            bid_won=bid_won,
        )

        return outcome

    def get_for_recommendation(self, recommendation_id: str) -> dict | None:
        """Look up the outcome for a given recommendation ID."""
        for outcome in self._load():
            if outcome.get("recommendation_id") == recommendation_id:
                return outcome
        return None

    def get_accuracy_summary(self) -> dict:
        """Compute prediction accuracy over all recorded outcomes.

        Returns:
            Dict with accuracy metrics.
        """
        outcomes = self._load()
        if not outcomes:
            return {"total": 0, "message": "No outcomes recorded yet"}

        total = len(outcomes)
        # Only outcomes where we have both recommendation and bid result
        evaluable = [
            o for o in outcomes
            if o.get("system_recommendation") and o.get("bid_submitted") is not None
        ]

        # Correct NO_BID: system said NO_BID and bid was either not submitted, or submitted and lost
        correct_no_bid = sum(
            1 for o in evaluable
            if o["system_recommendation"] == "NO_BID"
            and (not o["bid_submitted"] or o.get("bid_won") is False)
        )

        # Correct BID: system said BID and bid was submitted
        correct_bid = sum(
            1 for o in evaluable
            if o["system_recommendation"] == "BID" and o["bid_submitted"]
        )

        accuracy = (correct_no_bid + correct_bid) / len(evaluable) if evaluable else 0.0

        return {
            "total_outcomes": total,
            "evaluable_outcomes": len(evaluable),
            "accuracy": round(accuracy, 3),
            "correct_no_bid": correct_no_bid,
            "correct_bid": correct_bid,
        }

    def _load(self) -> list[dict]:
        if not self.outcomes_path.exists():
            return []
        return load_json(self.outcomes_path)

    def _initialize_if_empty(self) -> None:
        if not self.outcomes_path.exists():
            save_json([], self.outcomes_path)
