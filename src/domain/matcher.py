from __future__ import annotations

from dataclasses import dataclass

from .extractor import TenderDomainSignals
from .taxonomy import SECTOR_TO_BRANCH


@dataclass
class MatchResult:
    status: str  # "MATCH", "MISMATCH", "UNCERTAIN"
    company_branches: list[str]
    tender_branch: str | None
    reason: str


class DomainMatcher:
    def extract_company_branches(self, company_profile: dict) -> list[str]:
        branches: set[str] = set()

        sector = company_profile.get("sector", "")
        if sector:
            mapped = SECTOR_TO_BRANCH.get(sector) or SECTOR_TO_BRANCH.get(sector.lower())
            if mapped:
                branches.add(mapped)

        for project in company_profile.get("completed_projects", []):
            proj_sector = project.get("sector", "")
            if proj_sector:
                mapped = SECTOR_TO_BRANCH.get(proj_sector) or SECTOR_TO_BRANCH.get(proj_sector.lower())
                if mapped:
                    branches.add(mapped)

        return list(branches)

    def match(self, company_profile: dict, tender_signals: TenderDomainSignals) -> MatchResult:
        company_branches = self.extract_company_branches(company_profile)

        if not tender_signals.primary_branch:
            return MatchResult(
                status="UNCERTAIN",
                company_branches=company_branches,
                tender_branch=None,
                reason="Tender domain could not be determined from available signals.",
            )

        if not company_branches:
            return MatchResult(
                status="UNCERTAIN",
                company_branches=[],
                tender_branch=tender_signals.primary_branch,
                reason="Company domain profile is empty; cannot assess domain fit.",
            )

        if tender_signals.primary_branch in company_branches:
            return MatchResult(
                status="MATCH",
                company_branches=company_branches,
                tender_branch=tender_signals.primary_branch,
                reason=(
                    f"Tender primary domain '{tender_signals.primary_branch}' "
                    f"matches company domain."
                ),
            )

        secondary_match = [b for b in tender_signals.secondary_branches if b in company_branches]
        if secondary_match and not tender_signals.is_clear:
            return MatchResult(
                status="UNCERTAIN",
                company_branches=company_branches,
                tender_branch=tender_signals.primary_branch,
                reason=(
                    f"Tender primary domain '{tender_signals.primary_branch}' does not match, "
                    f"but secondary domain '{secondary_match[0]}' overlaps. "
                    "Domain signal is ambiguous."
                ),
            )

        return MatchResult(
            status="MISMATCH",
            company_branches=company_branches,
            tender_branch=tender_signals.primary_branch,
            reason=(
                f"Tender domain '{tender_signals.primary_branch}' does not match "
                f"company domain(s): {', '.join(company_branches)}."
            ),
        )
