#!/usr/bin/env python3
"""Batch ingest tender PDFs into the data/incoming/ directory.

Scans an input directory for PDF files and moves them to data/incoming/
so the folder watcher or CI pipeline can process them.

Usage:
    python scripts/ingest_tenders.py --input /path/to/tender/downloads/
    python scripts/ingest_tenders.py --input /downloads --dry-run
"""

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import get_config
from src.utils.helpers import ensure_dir
from src.utils.logger import configure_logging, get_logger

logger = get_logger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ingest tender PDFs into the incoming directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Directory containing tender PDF files to ingest",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be moved without actually moving them",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    args = parser.parse_args()

    configure_logging(level=args.log_level, fmt="console")

    config = get_config()

    if not args.input.exists():
        print(f"Error: Input directory not found: {args.input}", file=sys.stderr)
        return 1

    pdfs = list(args.input.glob("*.pdf")) + list(args.input.glob("*.PDF"))

    if not pdfs:
        print(f"No PDF files found in: {args.input}")
        return 0

    print(f"Found {len(pdfs)} PDF(s) in {args.input}")

    if args.dry_run:
        print("\nDry run — would move:")
        for pdf in pdfs:
            dest = config.INCOMING_DIR / pdf.name
            print(f"  {pdf} → {dest}")
        return 0

    ensure_dir(config.INCOMING_DIR)
    moved = 0
    skipped = 0

    for pdf in pdfs:
        dest = config.INCOMING_DIR / pdf.name
        if dest.exists():
            print(f"  Skipping (already exists): {pdf.name}")
            skipped += 1
            continue
        shutil.copy2(str(pdf), str(dest))
        print(f"  Ingested: {pdf.name}")
        moved += 1

    print(f"\nDone: {moved} ingested, {skipped} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
