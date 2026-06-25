#!/usr/bin/env python3
"""Run the full pipeline on all parsed tenders with a given company profile.

Usage:
    python scripts/score_all.py --profile data/company-profiles/apex.json
    python scripts/score_all.py --profile data/sample-data/sample_company_profile.json --output reports/
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import get_config
from src.utils.helpers import ensure_dir, load_json, save_json
from src.utils.logger import configure_logging, get_logger

logger = get_logger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the qualification pipeline on all parsed tenders.",
    )
    parser.add_argument(
        "--profile",
        required=True,
        type=Path,
        help="Company profile JSON file",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Directory of parsed tender JSONs (default: data/parsed-tenders/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory for recommendations (default: data/outcomes/)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-score tenders that have already been scored",
    )
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    configure_logging(level=args.log_level, fmt="console")
    config = get_config()

    if not args.profile.exists():
        print(f"Error: Company profile not found: {args.profile}", file=sys.stderr)
        return 1

    input_dir = args.input or config.PARSED_DIR
    output_dir = args.output or config.OUTCOMES_DIR
    ensure_dir(output_dir)

    parsed_files = list(input_dir.glob("*.json"))
    if not parsed_files:
        print(f"No parsed tenders found in {input_dir}")
        return 0

    print(f"Scoring {len(parsed_files)} tender(s) with profile: {args.profile.name}")
    print()

    company_profile = load_json(args.profile)
    company_id = company_profile.get("company_id", "unknown")

    scored = 0
    skipped = 0
    failed = 0
    results_summary = []

    for parsed_path in parsed_files:
        tender_id = parsed_path.stem
        output_path = output_dir / f"{tender_id}_recommendation.json"

        if output_path.exists() and not args.force:
            print(f"  Skipping (already scored): {tender_id}")
            skipped += 1
            continue

        print(f"  Scoring: {tender_id}...", end=" ", flush=True)
        try:
            # For batch scoring from parsed JSON files, we need the original PDF
            # or re-run extraction. Here we run from the parsed text.
            parsed_data = load_json(parsed_path)
            clean_text = parsed_data.get("clean_text", "")

            if not clean_text:
                print("SKIPPED (no text)")
                skipped += 1
                continue

            # Import inline to avoid heavy startup for skipped files
            from src.extractor.metadata import MetadataExtractor
            from src.extractor.requirement_extractor import RequirementExtractor
            from src.qualification.eligibility import EligibilityChecker
            from src.recommendation.engine import RecommendationEngine
            from src.scoring.competitiveness import CompetitivenessScorer
            from src.scoring.execution_risk import ExecutionRiskScorer
            from src.scoring.incumbent_risk import IncumbentRiskScorer
            from src.scoring.qualification_score import QualificationScorer
            from src.scoring.value_score import ValueScorer
            from src.ledger.decisions import DecisionLedger

            metadata = MetadataExtractor().extract(clean_text)
            requirements = RequirementExtractor().extract(clean_text, tender_id=tender_id)
            eligibility = EligibilityChecker().check(requirements, company_profile)
            qual_score = QualificationScorer().score(eligibility)
            competitive = CompetitivenessScorer().score(company_profile, metadata.contract_value_inr, metadata.tender_type, len(requirements))
            incumbent = IncumbentRiskScorer().score(clean_text, metadata.contract_duration_months)
            execution = ExecutionRiskScorer().score(clean_text, company_profile, metadata.contract_duration_months, len(requirements), qual_score)
            value = ValueScorer().score(company_profile, metadata.contract_value_inr, metadata.tender_type, qual_score, competitive, incumbent)
            rec = RecommendationEngine().recommend(eligibility, tender_id, company_id, competitive, incumbent, execution, value)
            DecisionLedger().append(rec)
            save_json(rec.to_dict(), output_path)

            print(f"{rec.recommendation} (score: {rec.qualification_score})")
            results_summary.append({
                "tender_id": tender_id,
                "recommendation": rec.recommendation,
                "qualification_score": rec.qualification_score,
            })
            scored += 1
        except Exception as exc:
            print(f"FAILED: {exc}")
            logger.error("score_failed", tender=tender_id, error=str(exc))
            failed += 1

    print(f"\nResults: {scored} scored, {skipped} skipped, {failed} failed")

    if results_summary:
        print("\nSummary:")
        bid = sum(1 for r in results_summary if r["recommendation"] == "BID")
        review = sum(1 for r in results_summary if r["recommendation"] == "REVIEW")
        no_bid = sum(1 for r in results_summary if r["recommendation"] == "NO_BID")
        print(f"  BID:    {bid}")
        print(f"  REVIEW: {review}")
        print(f"  NO BID: {no_bid}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
