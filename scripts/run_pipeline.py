#!/usr/bin/env python3
"""Run the complete qualification pipeline on a single tender PDF.

Usage:
    python scripts/run_pipeline.py --pdf path/to/tender.pdf --profile path/to/company.json
    python scripts/run_pipeline.py --pdf data/incoming/tender.pdf --profile data/company-profiles/apex.json
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.runner import PipelineRunner
from src.utils.logger import configure_logging


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Tender Qualification Assistant pipeline on a single tender.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--pdf",
        required=True,
        type=Path,
        help="Path to the tender PDF file",
    )
    parser.add_argument(
        "--profile",
        required=True,
        type=Path,
        help="Path to the company profile JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional: save recommendation JSON to this path (default: print to stdout)",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: WARNING — suppress pipeline noise)",
    )
    args = parser.parse_args()

    configure_logging(level=args.log_level, fmt="console")

    if not args.pdf.exists():
        print(f"Error: PDF not found: {args.pdf}", file=sys.stderr)
        return 1
    if not args.profile.exists():
        print(f"Error: Company profile not found: {args.profile}", file=sys.stderr)
        return 1

    print(f"Processing: {args.pdf.name}")
    print(f"Profile:    {args.profile.name}")
    print()

    try:
        runner = PipelineRunner()
        recommendation = runner.run(args.pdf, args.profile)
    except Exception as exc:
        print(f"Pipeline error: {exc}", file=sys.stderr)
        return 1

    # Print summary
    print("=" * 60)
    print(f"RECOMMENDATION: {recommendation.recommendation}")
    print(f"Qualification Score: {recommendation.qualification_score}/100")
    if recommendation.competitive_strength is not None:
        print(f"Competitive Strength: {recommendation.competitive_strength}/100")
    if recommendation.incumbent_risk is not None:
        print(f"Incumbent Risk: {recommendation.incumbent_risk}/100")
    if recommendation.execution_risk is not None:
        print(f"Execution Risk: {recommendation.execution_risk}/100")
    if recommendation.value_score is not None:
        print(f"Value Score: {recommendation.value_score}/100")
    print(f"Confidence: {recommendation.confidence:.2f}")

    if recommendation.primary_bottleneck:
        print(f"\nPrimary Bottleneck: {recommendation.primary_bottleneck}")

    if recommendation.evidence_gaps:
        print("\nEvidence Gaps:")
        for gap in recommendation.evidence_gaps:
            print(f"  - {gap}")

    if recommendation.reasoning:
        print(f"\nReasoning:\n{recommendation.reasoning}")

    print("=" * 60)

    # Save to file if requested
    if args.output:
        import json as json_mod

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json_mod.dump(recommendation.to_dict(), f, indent=2, ensure_ascii=False, default=str)
        print(f"\nSaved to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
