"""Split tender text into numbered clauses for structured processing."""

import re
from dataclasses import dataclass

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Patterns for Indian government tender clause numbering
CLAUSE_PATTERNS = [
    # Standard numbered clauses: 1.2.3, Section 3.1, Clause 4.2
    r"(?:^|\n)(?:Section|Clause|Para|Paragraph|Article)?\s*(\d+(?:\.\d+)*)\s*[.\-:]?\s+([A-Z][^\n]{3,80})",
    # Lettered sections: A. Introduction, B. Scope
    r"(?:^|\n)([A-Z])\.\s+([A-Z][^\n]{3,80})",
    # Roman numeral sections: I. II. III.
    r"(?:^|\n)((?:I{1,3}|IV|V?I{0,3}|IX|X))\.\s+([A-Z][^\n]{3,80})",
    # ALL CAPS section headings (common in Indian tenders)
    r"(?:^|\n)([A-Z][A-Z ]{5,60})\n",
]

# Compiled pattern for clause number detection
CLAUSE_NUMBER_RE = re.compile(
    r"^(?:Section|Clause|Para|Paragraph|Article)?\s*(\d+(?:\.\d+){0,3})\s*[.\-:]\s*",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass
class Clause:
    """A single numbered clause from a tender document."""

    clause_number: str
    heading: str
    text: str
    start_pos: int


class ClauseExtractor:
    """Splits tender document text into individual numbered clauses.

    Recognizes clause numbering patterns common in Indian government tenders
    following GFR 2017, CPPP, and state procurement rule formats.
    """

    def extract_clauses(self, text: str) -> list[dict]:
        """Split tender text into a list of clause dictionaries.

        Args:
            text: Cleaned tender document text.

        Returns:
            List of clause dicts with keys: clause_number, heading, text, start_pos.
        """
        if not text.strip():
            return []

        splits = self._find_clause_boundaries(text)
        clauses = self._build_clause_list(text, splits)

        logger.debug("clauses_extracted", count=len(clauses))
        return [
            {
                "clause_number": c.clause_number,
                "heading": c.heading,
                "text": c.text,
                "start_pos": c.start_pos,
            }
            for c in clauses
        ]

    def _find_clause_boundaries(self, text: str) -> list[tuple[int, str, str]]:
        """Find positions where new clauses start.

        Returns:
            List of (position, clause_number, heading) tuples.
        """
        boundaries: list[tuple[int, str, str]] = []

        for match in CLAUSE_NUMBER_RE.finditer(text):
            clause_num = match.group(1)
            # Extract heading: text from end of match to next newline
            rest = text[match.end() :].split("\n")[0].strip()
            heading = rest[:80] if rest else ""

            boundaries.append((match.start(), clause_num, heading))

        # Sort by position (should already be in order but be safe)
        boundaries.sort(key=lambda x: x[0])
        return boundaries

    def _build_clause_list(
        self,
        text: str,
        boundaries: list[tuple[int, str, str]],
    ) -> list[Clause]:
        """Build Clause objects from the text and boundary positions."""
        if not boundaries:
            # No clause structure found — return the whole text as one clause
            return [Clause(clause_number="0", heading="Full Document", text=text, start_pos=0)]

        clauses: list[Clause] = []
        for i, (start, num, heading) in enumerate(boundaries):
            end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(text)
            clause_text = text[start:end].strip()
            clauses.append(
                Clause(
                    clause_number=num,
                    heading=heading,
                    text=clause_text,
                    start_pos=start,
                )
            )

        return clauses

    def extract_eligibility_section(self, text: str) -> str:
        """Extract the eligibility / pre-qualification section from the tender.

        Looks for common headings used for eligibility criteria in Indian tenders.

        Args:
            text: Full tender text.

        Returns:
            The eligibility section text, or the full text if not found.
        """
        eligibility_keywords = [
            "eligibility criteria",
            "pre-qualification criteria",
            "prequalification criteria",
            "qualifying criteria",
            "bid qualification",
            "mandatory requirements",
            "vendor qualification",
        ]

        lines = text.split("\n")
        start_idx: int | None = None
        end_idx: int | None = None

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(kw in line_lower for kw in eligibility_keywords):
                if start_idx is None:
                    start_idx = i
            elif start_idx is not None:
                # Look for the next major section heading to end the eligibility block
                if re.match(r"^\d+\.\s+[A-Z]", line) and i > start_idx + 5:
                    end_idx = i
                    break

        if start_idx is not None:
            end = end_idx or min(start_idx + 200, len(lines))
            eligibility_text = "\n".join(lines[start_idx:end])
            logger.debug(
                "eligibility_section_found",
                start_line=start_idx,
                end_line=end,
                chars=len(eligibility_text),
            )
            return eligibility_text

        logger.debug("eligibility_section_not_found_using_full_text")
        return text
