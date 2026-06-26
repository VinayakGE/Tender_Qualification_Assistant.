from __future__ import annotations

from dataclasses import dataclass

from .extractor import DomainExtractor
from .matcher import DomainMatcher


@dataclass
class DomainFitResult:
    decision: str  # "PASS", "FAIL", "UNCERTAIN"
    company_branches: list[str]
    tender_branch: str | None
    tender_signals: dict[str, int]
    reason: str
    confidence: float


class DomainFitGate:
    def __init__(self) -> None:
        self._extractor = DomainExtractor()
        self._matcher = DomainMatcher()

    def evaluate(self, text: str, company_profile: dict) -> DomainFitResult:
        tender_signals = self._extractor.extract(text)
        match_result = self._matcher.match(company_profile, tender_signals)

        nonzero_scores = {k: v for k, v in tender_signals.branch_scores.items() if v > 0}

        if match_result.status == "MATCH":
            confidence = 0.90 if tender_signals.is_clear else 0.75
            return DomainFitResult(
                decision="PASS",
                company_branches=match_result.company_branches,
                tender_branch=match_result.tender_branch,
                tender_signals=nonzero_scores,
                reason=match_result.reason,
                confidence=confidence,
            )

        if match_result.status == "MISMATCH":
            confidence = 0.92 if tender_signals.is_clear else 0.78
            return DomainFitResult(
                decision="FAIL",
                company_branches=match_result.company_branches,
                tender_branch=match_result.tender_branch,
                tender_signals=nonzero_scores,
                reason=match_result.reason,
                confidence=confidence,
            )

        return DomainFitResult(
            decision="UNCERTAIN",
            company_branches=match_result.company_branches,
            tender_branch=match_result.tender_branch,
            tender_signals=nonzero_scores,
            reason=match_result.reason,
            confidence=0.50,
        )
