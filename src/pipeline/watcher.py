"""Folder watcher — automatically triggers the pipeline when a PDF is dropped in data/incoming/."""

import shutil
import time
from pathlib import Path

from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from src.pipeline.runner import PipelineRunner
from src.utils.config import get_config
from src.utils.helpers import ensure_dir
from src.utils.logger import configure_logging, get_logger

logger = get_logger(__name__)


class TenderDropHandler(FileSystemEventHandler):
    """Handles file creation events in the incoming directory.

    When a PDF appears, looks for a matching company profile and runs the pipeline.

    Naming convention:
        Tender PDF:       data/incoming/my_tender.pdf
        Company profile:  data/company-profiles/my_tender_profile.json

    If no matching profile is found, uses the default profile (if it exists):
        data/company-profiles/default_profile.json
    """

    def __init__(self) -> None:
        self.config = get_config()
        self.runner = PipelineRunner()
        ensure_dir(self.config.RAW_DIR)

    def on_created(self, event: FileCreatedEvent) -> None:
        """Called when a file is created in the watched directory."""
        if event.is_directory:
            return

        path = Path(event.src_path)
        if path.suffix.lower() != ".pdf":
            logger.debug("watcher_non_pdf_ignored", path=str(path))
            return

        logger.info("watcher_new_pdf_detected", path=str(path))
        self._process(path)

    def _process(self, pdf_path: Path) -> None:
        """Process a new tender PDF through the pipeline."""
        profile_path = self._find_profile(pdf_path)

        if profile_path is None:
            logger.error(
                "watcher_no_profile_found",
                pdf_path=str(pdf_path),
                message="Skipping — no matching company profile. "
                        "Create data/company-profiles/<stem>_profile.json or default_profile.json",
            )
            return

        try:
            recommendation = self.runner.run(pdf_path, profile_path)
            logger.info(
                "watcher_pipeline_complete",
                pdf=pdf_path.name,
                recommendation=recommendation.recommendation,
                qualification_score=recommendation.qualification_score,
            )

            # Move PDF to raw-tenders after successful processing
            dest = self.config.RAW_DIR / pdf_path.name
            shutil.move(str(pdf_path), str(dest))
            logger.info("watcher_pdf_moved", from_path=str(pdf_path), to_path=str(dest))

        except Exception as exc:
            logger.error(
                "watcher_pipeline_error",
                pdf_path=str(pdf_path),
                error=str(exc),
                exc_info=True,
            )

    def _find_profile(self, pdf_path: Path) -> Path | None:
        """Find the company profile for a given tender PDF.

        Looks for: data/company-profiles/<stem>_profile.json
        Falls back to: data/company-profiles/default_profile.json
        """
        profiles_dir = self.config.COMPANY_PROFILES_DIR

        # Primary: <stem>_profile.json
        primary = profiles_dir / f"{pdf_path.stem}_profile.json"
        if primary.exists():
            logger.debug("watcher_profile_found", profile=str(primary))
            return primary

        # Fallback: default_profile.json
        default = profiles_dir / "default_profile.json"
        if default.exists():
            logger.info(
                "watcher_using_default_profile",
                pdf=pdf_path.name,
                profile=str(default),
            )
            return default

        return None


class FolderWatcher:
    """Watches data/incoming/ for new tender PDFs and runs the pipeline automatically."""

    def __init__(self) -> None:
        self.config = get_config()
        ensure_dir(self.config.INCOMING_DIR)

    def start(self, block: bool = True) -> None:
        """Start watching the incoming directory.

        Args:
            block: If True, blocks until interrupted (Ctrl+C). If False, runs in background.
        """
        handler = TenderDropHandler()
        observer = Observer()
        observer.schedule(handler, str(self.config.INCOMING_DIR), recursive=False)
        observer.start()

        logger.info(
            "watcher_started",
            watching=str(self.config.INCOMING_DIR),
        )

        if not block:
            return

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("watcher_stopping")
            observer.stop()
        observer.join()
        logger.info("watcher_stopped")


if __name__ == "__main__":
    configure_logging()
    watcher = FolderWatcher()
    watcher.start()
