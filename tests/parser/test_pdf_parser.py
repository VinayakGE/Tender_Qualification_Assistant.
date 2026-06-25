"""Tests for PDF parser and text cleaner."""

import pytest

from src.parser.cleaner import TextCleaner
from src.parser.pdf_parser import PDFParser


class TestPDFParser:
    def test_raises_file_not_found(self, tmp_path):
        """Parser raises FileNotFoundError for a non-existent PDF."""
        parser = PDFParser()
        with pytest.raises(FileNotFoundError, match="PDF not found"):
            parser.extract_text(tmp_path / "nonexistent.pdf")

    def test_count_pages_nonexistent_returns_zero(self, tmp_path):
        """_count_pages returns 0 for a file that cannot be opened."""
        parser = PDFParser()
        # A non-PDF file will fail silently and return 0
        fake_pdf = tmp_path / "fake.pdf"
        fake_pdf.write_bytes(b"not a real pdf")
        result = parser._count_pages(fake_pdf)
        assert result == 0


class TestTextCleaner:
    def test_clean_strips_extra_whitespace(self):
        """Cleaner collapses multiple blank lines."""
        raw = "Line one\n\n\n\n\nLine two"
        cleaner = TextCleaner()
        cleaned = cleaner.clean(raw)
        assert "\n\n\n" not in cleaned
        assert "Line one" in cleaned
        assert "Line two" in cleaned

    def test_clean_empty_input_returns_empty(self):
        """Cleaner returns empty string for empty input."""
        cleaner = TextCleaner()
        assert cleaner.clean("") == ""
        assert cleaner.clean("   \n\n   ") == ""

    def test_clean_fixes_encoding_artifacts(self):
        """Cleaner replaces common encoding artifacts."""
        raw = "Companyâ€™s profile and â€œsatisfactoryâ€ performance"
        cleaner = TextCleaner()
        cleaned = cleaner.clean(raw)
        assert "â€™" not in cleaned
        assert "â€œ" not in cleaned

    def test_clean_removes_repeated_headers(self):
        """Cleaner removes lines that appear 3+ times (headers/footers)."""
        # Simulate a repeated footer
        repeated = "Ministry of Finance | Page"
        raw = f"Section 1\n{repeated}\n\nSection 2\n{repeated}\n\nSection 3\n{repeated}\n"
        cleaner = TextCleaner()
        cleaned = cleaner.clean(raw)
        # Should appear 0 times after cleaning
        assert cleaned.count(repeated) == 0

    def test_clean_rejoins_hyphenated_words(self):
        """Cleaner rejoins words split by hyphen-newline."""
        raw = "The quali-\nfication criteria must be met"
        cleaner = TextCleaner()
        cleaned = cleaner.clean(raw)
        assert "qualification" in cleaned

    def test_clean_removes_standalone_page_numbers(self):
        """Cleaner removes standalone page number lines."""
        raw = "Section 3\n\n- 5 -\n\nSection 4"
        cleaner = TextCleaner()
        cleaned = cleaner.clean(raw)
        assert "- 5 -" not in cleaned

    def test_clean_preserves_clause_numbers(self):
        """Cleaner does not strip clause numbers."""
        raw = "3.1 The bidder shall have annual turnover of Rs. 30 Cr."
        cleaner = TextCleaner()
        cleaned = cleaner.clean(raw)
        assert "3.1" in cleaned
        assert "30 Cr" in cleaned
