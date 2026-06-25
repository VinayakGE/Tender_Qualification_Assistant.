"""Evidence store — persists and retrieves evidence items."""

from pathlib import Path

from src.utils.config import get_config
from src.utils.helpers import ensure_dir, generate_id, load_json, save_json
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EvidenceStore:
    """Stores evidence items for each recommendation.

    Evidence items are stored as JSON files in the outcomes directory,
    named by recommendation_id: data/outcomes/{rec_id}_evidence.json
    """

    def __init__(self) -> None:
        self.config = get_config()
        ensure_dir(self.config.OUTCOMES_DIR)

    def save(self, recommendation_id: str, evidence_items: list[dict]) -> Path:
        """Save evidence items for a recommendation.

        Args:
            recommendation_id: The recommendation these items belong to.
            evidence_items: List of evidence item dicts.

        Returns:
            Path to the saved evidence file.
        """
        # Ensure all items have IDs
        for item in evidence_items:
            if not item.get("evidence_id"):
                item["evidence_id"] = generate_id("ev")

        evidence_path = self.config.OUTCOMES_DIR / f"{recommendation_id}_evidence.json"
        save_json(evidence_items, evidence_path)

        logger.info(
            "evidence_saved",
            recommendation_id=recommendation_id,
            item_count=len(evidence_items),
            path=str(evidence_path),
        )

        return evidence_path

    def load(self, recommendation_id: str) -> list[dict]:
        """Load evidence items for a recommendation.

        Args:
            recommendation_id: The recommendation ID.

        Returns:
            List of evidence item dicts, or empty list if not found.
        """
        evidence_path = self.config.OUTCOMES_DIR / f"{recommendation_id}_evidence.json"
        if not evidence_path.exists():
            return []

        return load_json(evidence_path)

    def list_gaps(self, recommendation_id: str) -> list[dict]:
        """Return only the evidence items where gap=True.

        Args:
            recommendation_id: The recommendation ID.

        Returns:
            List of gap evidence items.
        """
        items = self.load(recommendation_id)
        return [item for item in items if item.get("gap", False)]
