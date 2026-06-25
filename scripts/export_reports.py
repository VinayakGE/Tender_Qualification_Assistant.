#!/usr/bin/env python3
"""Export a Markdown summary report from the decision ledger.

Usage:
    python scripts/export_reports.py
    python scripts/export_reports.py --output reports/decisions.md
    python scripts/export_reports.py --filter BID
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.helpers import ensure_dir
from src.utils.logger import configure_logging


def format_score_bar(score: int | None, width: int = 20) -> str:
    """Render a text progress bar for a score."""
    if score is None:
        return "N/A"
    filled = int((score / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar} {score}/100"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export a Markdown summary of the decision ledger.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output Markdown file path (default: print to stdout)",
    )
    parser.add_argument(
        "--filter",
        choices=["BID", "REVIEW", "NO_BID"],
        default=None,
        help="Filter to only show decisions with this recommendation",
    )
    parser.add_argument(
        "--last",
        type=int,
        default=None,
        help="Show only the last N decisions",
    )
    args = parser.parse_args()

    configure_logging(level="WARNING", fmt="console")

    from src.ledger.decisions import DecisionLedger

    ledger = DecisionLedger()
    entries = ledger.read_all()

    if not entries:
        print("No decisions in ledger yet.")
        return 0

    # Apply filters
    if args.filter:
        entries = [e for e in entries if e.get("recommendation") == args.filter]
    if args.last:
        entries = entries[-args.last :]

    # Build Markdown
    lines = []
    lines.append("# Tender Qualification Decision Report")
    lines.append(f"\nGenerated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"Total decisions: {len(entries)}")

    if entries:
        bid = sum(1 for e in entries if e.get("recommendation") == "BID")
        review = sum(1 for e in entries if e.get("recommendation") == "REVIEW")
        no_bid = sum(1 for e in entries if e.get("recommendation") == "NO_BID")
        lines.append(f"\n**BID:** {bid} | **REVIEW:** {review} | **NO BID:** {no_bid}")

    lines.append("\n---\n")

    for entry in reversed(entries):  # Newest first
        rec = entry.get("recommendation", "?")
        tender_id = entry.get("tender_id", "?")
        company_id = entry.get("company_id", "?")
        qual_score = entry.get("qualification_score")
        incumbent = entry.get("incumbent_risk")
        bottleneck = entry.get("primary_bottleneck", "")
        created_at = entry.get("created_at", "")
        confidence = entry.get("confidence")
        reasoning = entry.get("reasoning", "")
        gaps = entry.get("evidence_gaps", [])

        lines.append(f"## {rec} — {tender_id}")
        lines.append(f"\n**Company:** {company_id}  ")
        lines.append(f"**Date:** {created_at}  ")
        lines.append(f"**Confidence:** {confidence:.2f if confidence else 'N/A'}")

        lines.append("\n| Score | Value |")
        lines.append("|---|---|")
        lines.append(f"| Qualification | {format_score_bar(qual_score)} |")
        if entry.get("competitive_strength") is not None:
            lines.append(
                f"| Competitive Strength | {format_score_bar(entry['competitive_strength'])} |"
            )
        if incumbent is not None:
            lines.append(f"| Incumbent Risk | {format_score_bar(incumbent)} |")
        if entry.get("execution_risk") is not None:
            lines.append(f"| Execution Risk | {format_score_bar(entry['execution_risk'])} |")
        if entry.get("value_score") is not None:
            lines.append(f"| Value Score | {format_score_bar(entry['value_score'])} |")

        if bottleneck:
            lines.append(f"\n**Primary Bottleneck:** {bottleneck}")

        if gaps:
            lines.append("\n**Evidence Gaps:**")
            for gap in gaps:
                lines.append(f"- {gap}")

        if reasoning:
            lines.append(f"\n> {reasoning}")

        lines.append("\n---\n")

    report = "\n".join(lines)

    if args.output:
        ensure_dir(args.output.parent)
        args.output.write_text(report, encoding="utf-8")
        print(f"Report saved to: {args.output}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
