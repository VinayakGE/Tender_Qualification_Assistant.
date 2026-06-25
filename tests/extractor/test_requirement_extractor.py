"""Tests for requirement extractor — clause splitting and LLM extraction."""

from unittest.mock import MagicMock, patch

import pytest

from src.extractor.clause_extractor import ClauseExtractor
from src.extractor.requirement_extractor import Requirement, RequirementExtractor


class TestClauseExtractor:
    def test_extracts_numbered_clauses(self, sample_tender_text):
        """ClauseExtractor finds numbered clauses in tender text."""
        extractor = ClauseExtractor()
        clauses = extractor.extract_clauses(sample_tender_text)
        # Should find multiple clauses (1.1, 1.2, 1.3, 1.4, 2, 3)
        assert len(clauses) >= 3
        clause_numbers = {c["clause_number"] for c in clauses}
        assert "1" in clause_numbers or "1.1" in clause_numbers

    def test_returns_single_clause_for_unstructured_text(self):
        """Returns one clause for text with no numbered structure."""
        extractor = ClauseExtractor()
        clauses = extractor.extract_clauses("Just some plain text with no clauses.")
        assert len(clauses) == 1
        assert clauses[0]["clause_number"] == "0"

    def test_empty_text_returns_empty(self):
        """Returns empty list for empty text."""
        extractor = ClauseExtractor()
        assert extractor.extract_clauses("") == []

    def test_extract_eligibility_section(self, sample_tender_text):
        """Extracts the eligibility section from the tender."""
        extractor = ClauseExtractor()
        section = extractor.extract_eligibility_section(sample_tender_text)
        assert "ELIGIBILITY" in section.upper() or "turnover" in section.lower()

    def test_clauses_have_required_keys(self, sample_tender_text):
        """Each clause dict has the required keys."""
        extractor = ClauseExtractor()
        clauses = extractor.extract_clauses(sample_tender_text)
        for clause in clauses:
            assert "clause_number" in clause
            assert "heading" in clause
            assert "text" in clause
            assert "start_pos" in clause


class TestRequirementExtractor:
    """Tests for RequirementExtractor — uses mocked Claude API."""

    MOCK_RESPONSE = """[
        {
            "requirement_id": "req_001",
            "category": "turnover",
            "description": "Average annual turnover of Rs. 30 Crores over last 3 years",
            "threshold_value": 30.0,
            "threshold_unit": "INR_crores",
            "threshold_period_years": 3,
            "is_mandatory": true,
            "source_clause": "1.1",
            "raw_text": "average annual turnover of not less than Rs. 30 Crores",
            "certification_name": null,
            "sector": null
        },
        {
            "requirement_id": "req_002",
            "category": "certification",
            "description": "ISO 9001:2015 certification",
            "threshold_value": null,
            "threshold_unit": null,
            "threshold_period_years": null,
            "is_mandatory": true,
            "source_clause": "1.3",
            "raw_text": "must hold valid ISO 9001:2015 certification",
            "certification_name": "ISO 9001:2015",
            "sector": null
        }
    ]"""

    def test_extract_returns_requirements(self, tmp_path, sample_tender_text):
        """RequirementExtractor returns a list of Requirement objects."""
        # Create a minimal prompt file
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        prompt_file = prompts_dir / "requirement-extractor.md"
        prompt_file.write_text("Some preamble\n```\n{tender_text}\n```\n", encoding="utf-8")

        with patch("src.extractor.requirement_extractor.get_config") as mock_config:
            mock_cfg = MagicMock()
            mock_cfg.ANTHROPIC_API_KEY = "test-key"
            mock_cfg.MODEL = "claude-sonnet-4-6"
            mock_cfg.MAX_TOKENS = 4096
            mock_cfg.PROMPTS_DIR = prompts_dir
            mock_config.return_value = mock_cfg

            extractor = RequirementExtractor()

            # Mock the Anthropic client
            with patch.object(extractor, "_call_claude", return_value=self.MOCK_RESPONSE):
                requirements = extractor.extract(sample_tender_text, tender_id="T001")

        assert len(requirements) == 2
        assert all(isinstance(r, Requirement) for r in requirements)
        assert requirements[0].category == "turnover"
        assert requirements[0].threshold_value == 30.0
        assert requirements[0].is_mandatory is True
        assert requirements[1].category == "certification"
        assert requirements[1].certification_name == "ISO 9001:2015"

    def test_parse_response_handles_markdown_fences(self, tmp_path):
        """Parser strips markdown code fences from LLM response."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        prompt_file = prompts_dir / "requirement-extractor.md"
        prompt_file.write_text("```\n{tender_text}\n```\n", encoding="utf-8")

        with patch("src.extractor.requirement_extractor.get_config") as mock_config:
            mock_cfg = MagicMock()
            mock_cfg.ANTHROPIC_API_KEY = "test-key"
            mock_cfg.MODEL = "claude-sonnet-4-6"
            mock_cfg.MAX_TOKENS = 4096
            mock_cfg.PROMPTS_DIR = prompts_dir
            mock_config.return_value = mock_cfg

            extractor = RequirementExtractor()
            wrapped = f"```json\n{self.MOCK_RESPONSE}\n```"
            result = extractor._parse_response(wrapped, "T002")

        assert len(result) == 2

    def test_parse_response_invalid_json_raises(self, tmp_path):
        """Parser raises RuntimeError for invalid JSON response."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "requirement-extractor.md").write_text("```\n{tender_text}\n```\n")

        with patch("src.extractor.requirement_extractor.get_config") as mock_config:
            mock_cfg = MagicMock()
            mock_cfg.ANTHROPIC_API_KEY = "test-key"
            mock_cfg.PROMPTS_DIR = prompts_dir
            mock_config.return_value = mock_cfg

            extractor = RequirementExtractor()
            with pytest.raises(RuntimeError, match="Failed to parse"):
                extractor._parse_response("not json at all", "T003")

    def test_parse_response_skips_invalid_items(self, tmp_path):
        """Parser skips items with invalid categories but includes valid ones."""
        bad_response = """[
            {"requirement_id": "r1", "category": "INVALID_CAT", "description": "x", "is_mandatory": true},
            {"requirement_id": "r2", "category": "turnover", "description": "Annual turnover >= 10 Cr",
             "threshold_value": 10.0, "threshold_unit": "INR_crores", "is_mandatory": true}
        ]"""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "requirement-extractor.md").write_text("```\n{tender_text}\n```\n")

        with patch("src.extractor.requirement_extractor.get_config") as mock_config:
            mock_cfg = MagicMock()
            mock_cfg.ANTHROPIC_API_KEY = "test-key"
            mock_cfg.PROMPTS_DIR = prompts_dir
            mock_config.return_value = mock_cfg

            extractor = RequirementExtractor()
            result = extractor._parse_response(bad_response, "T004")

        # Only the valid item should be returned
        assert len(result) == 1
        assert result[0].category == "turnover"
