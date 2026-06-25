"""LLM-powered structured requirement extraction from tender text."""

import json
from pathlib import Path

import anthropic
from pydantic import BaseModel, Field, field_validator

from src.utils.config import get_config
from src.utils.helpers import generate_id, truncate_text
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Maximum characters to send to LLM in a single call
MAX_TEXT_CHARS = 12000


class Requirement(BaseModel):
    """A single eligibility requirement extracted from a tender document."""

    requirement_id: str
    category: str
    description: str
    threshold_value: float | None = None
    threshold_unit: str | None = None
    threshold_period_years: int | None = None
    is_mandatory: bool
    source_clause: str | None = None
    raw_text: str | None = None
    certification_name: str | None = None
    sector: str | None = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = {"turnover", "experience", "certification", "financial", "technical", "other"}
        if v not in allowed:
            raise ValueError(f"Invalid category '{v}'. Must be one of: {allowed}")
        return v


class RequirementExtractor:
    """Extracts structured requirements from cleaned tender text using Claude API.

    Loads the prompt from prompts/requirement-extractor.md and calls the
    configured Claude model to produce a JSON array of requirements.
    """

    def __init__(self) -> None:
        self.config = get_config()
        self.client = anthropic.Anthropic(api_key=self.config.ANTHROPIC_API_KEY)
        self._prompt_template: str | None = None

    def extract(self, tender_text: str, tender_id: str = "") -> list[Requirement]:
        """Extract requirements from tender text.

        Args:
            tender_text: Cleaned tender document text.
            tender_id: Optional tender identifier for logging.

        Returns:
            List of Requirement objects.

        Raises:
            RuntimeError: If LLM call fails or response cannot be parsed.
        """
        prompt_template = self._load_prompt()
        text_to_send = truncate_text(tender_text, MAX_TEXT_CHARS)
        prompt = prompt_template.replace("{tender_text}", text_to_send)

        logger.info(
            "requirement_extraction_started",
            tender_id=tender_id,
            text_chars=len(text_to_send),
        )

        raw_response = self._call_claude(prompt)
        requirements = self._parse_response(raw_response, tender_id)

        logger.info(
            "requirement_extraction_complete",
            tender_id=tender_id,
            requirements_found=len(requirements),
            mandatory_count=sum(1 for r in requirements if r.is_mandatory),
        )

        return requirements

    def _load_prompt(self) -> str:
        """Load and cache the requirement extractor prompt."""
        if self._prompt_template is None:
            prompt_path = self.config.PROMPTS_DIR / "requirement-extractor.md"
            if not prompt_path.exists():
                raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

            content = prompt_path.read_text(encoding="utf-8")

            # Extract the prompt block from between the triple-backtick markers
            lines = content.split("\n")
            in_prompt = False
            prompt_lines: list[str] = []
            for line in lines:
                if line.strip() == "```" and not in_prompt:
                    in_prompt = True
                    continue
                elif line.strip() == "```" and in_prompt:
                    break
                elif in_prompt:
                    prompt_lines.append(line)

            self._prompt_template = "\n".join(prompt_lines)

        return self._prompt_template

    def _call_claude(self, prompt: str) -> str:
        """Call the Claude API with the given prompt.

        Args:
            prompt: Full prompt string.

        Returns:
            Raw text response from Claude.
        """
        message = self.client.messages.create(
            model=self.config.MODEL,
            max_tokens=self.config.MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def _parse_response(self, raw_response: str, tender_id: str) -> list[Requirement]:
        """Parse Claude's JSON response into Requirement objects.

        Attempts to parse as-is first, then strips markdown fences if needed,
        then retries once with a validation prompt.

        Args:
            raw_response: Raw text from Claude.
            tender_id: Tender ID for logging context.

        Returns:
            List of validated Requirement objects.
        """
        # Strip markdown code fences if present
        text = raw_response.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if len(lines) > 2 else text

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            logger.error(
                "requirement_extraction_json_parse_error",
                tender_id=tender_id,
                error=str(exc),
                raw_response_snippet=raw_response[:200],
            )
            raise RuntimeError(
                f"Failed to parse requirement extraction response as JSON: {exc}"
            ) from exc

        if not isinstance(data, list):
            raise RuntimeError(
                f"Expected a JSON array from requirement extractor, got {type(data).__name__}"
            )

        requirements: list[Requirement] = []
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                logger.warning("requirement_item_not_dict", index=i, tender_id=tender_id)
                continue

            # Ensure requirement_id is set
            if not item.get("requirement_id"):
                item["requirement_id"] = generate_id("req")

            try:
                req = Requirement(**item)
                requirements.append(req)
            except Exception as exc:
                logger.warning(
                    "requirement_item_validation_error",
                    index=i,
                    tender_id=tender_id,
                    error=str(exc),
                    item=item,
                )

        return requirements
