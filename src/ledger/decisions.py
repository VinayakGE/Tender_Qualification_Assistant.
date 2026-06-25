"""Thread-safe append-only decision ledger using a JSON file."""

import fcntl
import json
from pathlib import Path

from src.recommendation.engine import Recommendation
from src.utils.config import get_config
from src.utils.helpers import ensure_dir
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DecisionLedger:
    """Append-only ledger for qualification decisions.

    Stores all recommendations in decision-ledger.json.
    Uses fcntl file locking to be safe for concurrent writes.

    The ledger format is a JSON array:
    [
        { ...recommendation_dict... },
        { ...recommendation_dict... },
        ...
    ]

    Design note: This is intentionally simple for Phase 1-5. When the ledger
    exceeds ~10,000 entries, migrate to PostgreSQL (see docs/architecture.md).
    """

    def __init__(self, ledger_path: Path | None = None) -> None:
        self.config = get_config()
        self.ledger_path = ledger_path or self.config.LEDGER_FILE
        ensure_dir(self.ledger_path.parent)
        self._initialize_if_empty()

    def append(self, recommendation: Recommendation) -> None:
        """Append a recommendation to the ledger.

        Thread-safe via exclusive file lock.

        Args:
            recommendation: The Recommendation to append.
        """
        entry = recommendation.to_dict()

        with open(self.ledger_path, "r+", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                content = f.read()
                data: list = json.loads(content) if content.strip() else []
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                f.truncate()
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

        logger.info(
            "ledger_entry_appended",
            recommendation_id=recommendation.recommendation_id,
            recommendation=recommendation.recommendation,
            tender_id=recommendation.tender_id,
        )

    def read_all(self) -> list[dict]:
        """Read all entries from the ledger.

        Returns:
            List of recommendation dicts, newest-last.
        """
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                content = f.read()
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

        return json.loads(content) if content.strip() else []

    def read_paginated(self, page: int = 1, page_size: int = 20) -> tuple[list[dict], int]:
        """Read a page of entries from the ledger, newest first.

        Args:
            page: Page number (1-indexed).
            page_size: Number of entries per page.

        Returns:
            Tuple of (entries, total_count).
        """
        all_entries = self.read_all()
        all_entries.reverse()  # Newest first
        total = len(all_entries)
        start = (page - 1) * page_size
        end = start + page_size
        return all_entries[start:end], total

    def find_by_id(self, recommendation_id: str) -> dict | None:
        """Find a single entry by recommendation ID.

        Args:
            recommendation_id: The recommendation ID to look up.

        Returns:
            The recommendation dict, or None if not found.
        """
        for entry in self.read_all():
            if entry.get("recommendation_id") == recommendation_id:
                return entry
        return None

    def _initialize_if_empty(self) -> None:
        """Create an empty ledger file if it does not exist."""
        if not self.ledger_path.exists():
            with open(self.ledger_path, "w", encoding="utf-8") as f:
                json.dump([], f)
            logger.info("ledger_initialized", path=str(self.ledger_path))
