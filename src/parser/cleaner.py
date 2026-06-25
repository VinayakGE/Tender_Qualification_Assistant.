"""Text cleaning and normalization for tender document text."""

import re
from collections import Counter

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Minimum number of page occurrences for a line to be treated as a header/footer
HEADER_FOOTER_MIN_OCCURRENCES = 3


class TextCleaner:
    """Normalizes raw text extracted from tender PDFs.

    Handles:
    - Repeated page headers and footers
    - Excessive whitespace
    - Unicode encoding artifacts
    - Hyphenated line-break word splits
    """

    def clean(self, raw_text: str) -> str:
        """Clean and normalize tender document text.

        Args:
            raw_text: Raw text as extracted by PDFParser or OCRExtractor.

        Returns:
            Cleaned, normalized UTF-8 text.
        """
        if not raw_text or not raw_text.strip():
            logger.warning("cleaner_empty_input")
            return ""

        text = raw_text

        text = self._fix_encoding_artifacts(text)
        text = self._remove_repeated_headers_footers(text)
        text = self._rejoin_hyphenated_words(text)
        text = self._normalize_whitespace(text)
        text = self._remove_standalone_page_numbers(text)

        logger.debug(
            "text_cleaned",
            original_chars=len(raw_text),
            cleaned_chars=len(text),
        )
        return text.strip()

    def _fix_encoding_artifacts(self, text: str) -> str:
        """Fix common UTF-8/Latin-1 encoding artifacts from PDF extraction."""
        replacements = [
            ("â€™", "'"),  # â€™ → '
            ("â€œ", '"'),  # â€œ → "
            ("â€", '"'),  # â€ → "
            ("â€", "-"),  # â€" → -
            ("Â ", " "),  # Â  → space (non-breaking space)
            ("â€¦", "..."),  # â€¦ → ...
            ("﻿", ""),  # BOM
            ("\x00", ""),  # null bytes
        ]
        for bad, good in replacements:
            text = text.replace(bad, good)
        return text

    def _remove_repeated_headers_footers(self, text: str) -> str:
        """Detect and remove lines that appear on multiple pages (headers/footers).

        Splits the document into page-sized chunks, counts line occurrences,
        and removes lines that appear on 3+ pages.
        """
        lines = text.split("\n")
        # Use a sliding window to detect repetition without needing explicit page markers
        line_counts: Counter = Counter()
        for line in lines:
            stripped = line.strip()
            if stripped and len(stripped) < 120:  # Headers/footers are short
                line_counts[stripped] += 1

        repeated_lines = {
            line for line, count in line_counts.items() if count >= HEADER_FOOTER_MIN_OCCURRENCES
        }

        if repeated_lines:
            logger.debug("cleaner_removed_headers", count=len(repeated_lines))

        cleaned_lines = [line for line in lines if line.strip() not in repeated_lines]
        return "\n".join(cleaned_lines)

    def _rejoin_hyphenated_words(self, text: str) -> str:
        """Rejoin words that were hyphenated at line breaks.

        Matches patterns like "quali-\nfication" → "qualification".
        """
        # Pattern: word-hyphen at end of line, continuation at start of next line
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Collapse excessive whitespace and normalize line endings."""
        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Collapse more than 2 consecutive blank lines to 1
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove trailing whitespace on each line
        lines = [line.rstrip() for line in text.split("\n")]
        return "\n".join(lines)

    def _remove_standalone_page_numbers(self, text: str) -> str:
        """Remove lines that are just page numbers (e.g., "- 5 -", "Page 5 of 12")."""
        patterns = [
            r"^\s*-\s*\d+\s*-\s*$",  # - 5 -
            r"^\s*Page\s+\d+\s+of\s+\d+\s*$",  # Page 5 of 12
            r"^\s*\d+\s*$",  # standalone number (risky — only for very short lines)
        ]
        combined = re.compile("|".join(patterns), re.IGNORECASE | re.MULTILINE)
        return combined.sub("", text)
