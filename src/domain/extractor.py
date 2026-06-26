from __future__ import annotations

import re
from dataclasses import dataclass

from .taxonomy import DOMAIN_BRANCHES


@dataclass
class TenderDomainSignals:
    branch_scores: dict[str, int]
    primary_branch: str | None
    secondary_branches: list[str]
    raw_signals: list[str]

    @property
    def is_clear(self) -> bool:
        if not self.primary_branch:
            return False
        scores = sorted(self.branch_scores.values(), reverse=True)
        if len(scores) < 2:
            return scores[0] >= 2 if scores else False
        return scores[0] >= 2 * scores[1] if scores[1] > 0 else scores[0] >= 2

    @property
    def primary_score(self) -> int:
        if not self.primary_branch:
            return 0
        return self.branch_scores.get(self.primary_branch, 0)


class DomainExtractor:
    def extract(self, text: str) -> TenderDomainSignals:
        normalized = text.lower()
        branch_scores: dict[str, int] = {branch: 0 for branch in DOMAIN_BRANCHES}
        raw_signals: list[str] = []

        for branch_name, branch_data in DOMAIN_BRANCHES.items():
            for phrase in branch_data["multi_keywords"]:
                count = len(re.findall(re.escape(phrase.lower()), normalized))
                if count:
                    branch_scores[branch_name] += count * 2
                    raw_signals.extend([phrase] * count)

            for word in branch_data["single_keywords"]:
                count = len(re.findall(r"\b" + re.escape(word.lower()) + r"\b", normalized))
                if count:
                    branch_scores[branch_name] += count * 1

            for signal in branch_data["authoritative_signals"]:
                # Use word boundary if signal is all word-chars, plain search otherwise
                if re.match(r"^\w[\w\s]*\w$", signal) or re.match(r"^\w$", signal):
                    pattern = r"\b" + re.escape(signal) + r"\b"
                else:
                    pattern = re.escape(signal)
                count = len(re.findall(pattern, text))
                if count:
                    branch_scores[branch_name] += count * 3
                    raw_signals.extend([signal] * count)

        ranked = sorted(branch_scores.items(), key=lambda x: x[1], reverse=True)
        primary_branch: str | None = None
        secondary_branches: list[str] = []

        if ranked and ranked[0][1] > 0:
            primary_branch = ranked[0][0]
            primary_score = ranked[0][1]
            threshold = primary_score * 0.3
            secondary_branches = [b for b, s in ranked[1:] if s >= threshold and s > 0]

        return TenderDomainSignals(
            branch_scores=branch_scores,
            primary_branch=primary_branch,
            secondary_branches=secondary_branches,
            raw_signals=raw_signals,
        )
