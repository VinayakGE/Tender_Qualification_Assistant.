#!/usr/bin/env python3
"""Batch parse all PDFs in data/raw-tenders/ and save to data/parsed-tenders/.

Usage:
    python scripts/parse_all.py
    python scripts/parse_all.py --input data/raw-tenders/ --output data/parsed-tenders/
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser.cleaner import TextCleaner
from src.parser.pdf_parser import PDFParser
from src.utils.config import get_config
from src.utils.helpers import ensure_dir, now_iso, save_json, slugify
from src.utils.logger import configure_logging, get_logger

logger = get_logger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch parse all tender PDFs in raw-tenders/.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input directory (default: data/raw-tenders/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory (default: data/parsed-tenders/)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-parse files that have already been parsed",
    )
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    configure_logging(level=args.log_level, fmt="console")
    config = get_config()

    input_dir = args.input or config.RAW_DIR
    output_dir = args.output or config.PARSED_DIR

    ensure_dir(output_dir)

    pdfs = list(input_dir.glob("*.pdf")) + list(input_dir.glob("*.PDF"))

    if not pdfs:
        print(f"No PDFs found in {input_dir}")
        return 0

    print(f"Parsing {len(pdfs)} PDF(s) from {input_dir}...")

    pdf_parser = PDFParser()
    cleaner = TextCleaner()
    parsed = 0
    skipped = 0
    failed = 0

    for pdf_path in pdfs:
        tender_id = slugify(pdf_path.stem)
        output_path = output_dir / f"{tender_id}.json"

        if output_path.exists() and not args.force:
            print(f"  Skipping (already parsed): {pdf_path.name}")
            skipped += 1
            continue

        print(f"  Parsing: {pdf_path.name}...", end=" ", flush=True)
        try:
            raw_text = pdf_parser.extract_text(pdf_path)
            clean_text = cleaner.clean(raw_text)
            save_json(
                {
                    "tender_id": tender_id,
                    "source_file": pdf_path.name,
                    "clean_text": clean_text,
                    "raw_text_length": len(raw_text),
                    "clean_text_length": len(clean_text),
                    "parsed_at": now_iso(),
                },
                output_path,
            )
            print(f"OK ({len(clean_text):,} chars)")
            parsed += 1
        except Exception as exc:
            print(f"FAILED: {exc}")
            logger.error("parse_failed", pdf=str(pdf_path), error=str(exc))
            failed += 1

    print(f"\nResults: {parsed} parsed, {skipped} skipped, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
