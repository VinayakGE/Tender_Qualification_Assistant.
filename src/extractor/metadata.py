"""Extract tender metadata (title, authority, dates, value) from tender text."""

import re
from dataclasses import dataclass, field
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Common date formats in Indian government tenders
DATE_PATTERNS = [
    r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b",         # DD/MM/YYYY or DD-MM-YYYY
    r"\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b",          # YYYY-MM-DD
    r"\b(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\b",          # 15 June 2024
]

# Patterns for contract value extraction
VALUE_PATTERNS = [
    r"(?:estimated|approximate|contract)\s*(?:cost|value|amount)[^\d₹Rs.]*[₹Rs.]\s*([\d,]+(?:\.\d+)?)\s*(?:crore|cr|lakh|L)\b",
    r"[₹Rs.]\s*([\d,]+(?:\.\d+)?)\s*(?:crore|cr|lakh|L)\b",
    r"(?:value|amount)[^₹Rs.\d]*([\d,]+(?:\.\d+)?)\s*(?:crore|cr|lakh|L)\b",
]

# Contract duration patterns
DURATION_PATTERNS = [
    r"(?:contract\s+)?(?:period|duration)\s+(?:of\s+)?(\d+)\s*(?:months?|years?)\b",
    r"(\d+)\s*(?:months?|years?)\s+(?:contract|period|duration)\b",
]


@dataclass
class TenderMetadata:
    """Extracted metadata from a tender document."""

    title: str = ""
    authority: str = ""
    published_date: str | None = None
    submission_deadline: str | None = None
    contract_value_inr: float | None = None
    contract_duration_months: int | None = None
    tender_type: str | None = None
    tender_id_raw: str | None = None


class MetadataExtractor:
    """Extracts metadata fields from cleaned tender document text.

    Uses a combination of regex patterns and heuristics. For ambiguous cases,
    uses Claude API as a fallback.
    """

    def extract(self, text: str) -> TenderMetadata:
        """Extract tender metadata from text.

        Args:
            text: Cleaned tender document text.

        Returns:
            TenderMetadata dataclass with extracted fields.
        """
        metadata = TenderMetadata()

        metadata.title = self._extract_title(text)
        metadata.authority = self._extract_authority(text)
        metadata.submission_deadline = self._extract_deadline(text)
        metadata.contract_value_inr = self._extract_contract_value(text)
        metadata.contract_duration_months = self._extract_duration(text)
        metadata.tender_type = self._extract_tender_type(text)
        metadata.tender_id_raw = self._extract_tender_id(text)

        logger.debug(
            "metadata_extracted",
            title=metadata.title[:60] if metadata.title else None,
            authority=metadata.authority[:60] if metadata.authority else None,
            contract_value_inr=metadata.contract_value_inr,
            tender_type=metadata.tender_type,
        )

        return metadata

    def _extract_title(self, text: str) -> str:
        """Extract the tender title from the first meaningful lines."""
        # Try "Tender for ..." pattern
        m = re.search(
            r"(?:tender|bid|rfp|rfq|nit|enquiry)\s+(?:for|of|no\.?)\s+([^\n]{10,120})",
            text[:2000],
            re.IGNORECASE,
        )
        if m:
            return m.group(1).strip()

        # Fallback: first non-empty line after the document header
        lines = [l.strip() for l in text[:1000].split("\n") if l.strip() and len(l.strip()) > 10]
        return lines[0][:120] if lines else "Unknown Title"

    def _extract_authority(self, text: str) -> str:
        """Extract the issuing authority/department name."""
        patterns = [
            r"(?:issued\s+by|tendering\s+authority|procuring\s+entity)[:\s]+([^\n]{10,100})",
            r"(?:government\s+of|ministry\s+of|department\s+of|office\s+of)[^\n]{5,80}",
        ]
        for pattern in patterns:
            m = re.search(pattern, text[:3000], re.IGNORECASE)
            if m:
                return m.group(0).strip()[:100]
        return "Unknown Authority"

    def _extract_deadline(self, text: str) -> str | None:
        """Extract the bid submission deadline."""
        deadline_patterns = [
            r"(?:last\s+date|due\s+date|submission\s+(?:date|deadline))[^\d]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
            r"(?:last\s+date|due\s+date|closing\s+date)[^\d]*(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
        ]
        for pattern in deadline_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    def _extract_contract_value(self, text: str) -> float | None:
        """Extract estimated contract value and normalize to INR."""
        for pattern in VALUE_PATTERNS:
            m = re.search(pattern, text[:5000], re.IGNORECASE)
            if m:
                raw = m.group(1).replace(",", "")
                try:
                    value = float(raw)
                    full_match = m.group(0).lower()
                    if "lakh" in full_match or " l " in full_match:
                        value = value * 100_000
                    elif "crore" in full_match or " cr" in full_match:
                        value = value * 10_000_000
                    return value
                except ValueError:
                    continue
        return None

    def _extract_duration(self, text: str) -> int | None:
        """Extract contract duration and normalize to months."""
        for pattern in DURATION_PATTERNS:
            m = re.search(pattern, text[:5000], re.IGNORECASE)
            if m:
                try:
                    value = int(m.group(1))
                    if "year" in m.group(0).lower():
                        value = value * 12
                    return value
                except ValueError:
                    continue
        return None

    def _extract_tender_type(self, text: str) -> str | None:
        """Classify tender as works, goods, services, or composite."""
        sample = text[:3000].lower()
        works_kw = ["construction", "civil work", "erection", "installation", "infrastructure"]
        goods_kw = ["supply of", "purchase of", "procurement of", "equipment", "material"]
        services_kw = ["service", "consultancy", "maintenance", "operation", "amc", "support"]

        scores = {
            "works": sum(1 for kw in works_kw if kw in sample),
            "goods": sum(1 for kw in goods_kw if kw in sample),
            "services": sum(1 for kw in services_kw if kw in sample),
        }
        best = max(scores, key=lambda k: scores[k])
        return best if scores[best] > 0 else None

    def _extract_tender_id(self, text: str) -> str | None:
        """Extract the tender/NIT reference number."""
        patterns = [
            r"(?:tender\s+no\.?|nit\s+no\.?|bid\s+no\.?|ref\s+no\.?)[:\s]+([A-Z0-9\-/]{5,40})",
            r"(?:e-tender|etender)\s+(?:no\.?|id)[:\s]+([A-Z0-9\-/]{5,40})",
        ]
        for pattern in patterns:
            m = re.search(pattern, text[:2000], re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None
