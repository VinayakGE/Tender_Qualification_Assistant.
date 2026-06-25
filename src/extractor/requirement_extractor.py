"""Structured requirement extraction from tender text.

Uses the Claude API when ANTHROPIC_API_KEY is set; falls back to regex-based
heuristic extraction when running without a key (Milestone 0 / offline mode).
"""

import json
import re
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from src.utils.config import get_config
from src.utils.helpers import generate_id, truncate_text
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Maximum characters to send to LLM in a single call
MAX_TEXT_CHARS = 12000

# ---------------------------------------------------------------------------
# Regex patterns for offline heuristic extraction (Indian government tenders)
# ---------------------------------------------------------------------------

_TURNOVER_RE = re.compile(
    r"(?:average\s+annual\s+turnover|annual\s+turnover)"
    r".{0,120}?Rs\.?\s*([\d,]+(?:\.\d+)?)\s*(crore|lakh|cr\.?)",
    re.IGNORECASE | re.DOTALL,
)
_EXPERIENCE_RE = re.compile(
    r"(?:successfully\s+completed|at\s+least)\s+(?:at\s+least\s+)?"
    r"(?:(\w+)\s+\((\d+)\)|(\d+))\s+(?:similar\s+)?(?:works?|projects?|road|highway)",
    re.IGNORECASE,
)
_EXPERIENCE_VALUE_RE = re.compile(
    r"(?:value|cost|each|not\s+less\s+than)\s+(?:not\s+less\s+than\s+)?(?:Rs\.?\s*)?"
    r"([\d,]+(?:\.\d+)?)\s*(crore|lakh|cr\.?)",
    re.IGNORECASE,
)
_NETWORTH_RE = re.compile(
    r"net\s+worth.{0,180}?(?:not\s+(?:be\s+)?less\s+than|minimum|at\s+least)\s+(?:Rs\.?\s*)?"
    r"([\d,]+(?:\.\d+)?)\s*(crore|lakh|cr\.?)",
    re.IGNORECASE | re.DOTALL,
)
_ISO_RE = re.compile(r"\bISO\s+(\d{4}(?:[-:]\d{4})?)\b", re.IGNORECASE)
_CLAUSE_RE = re.compile(
    r"(?:Section|Clause|Para)\s+(\d+(?:\.\d+)*)", re.IGNORECASE
)


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
    """Extracts structured requirements from cleaned tender text.

    Uses Claude API when ANTHROPIC_API_KEY is configured; falls back to
    regex-based heuristic extraction otherwise (offline / Milestone 0 mode).
    """

    def __init__(self) -> None:
        self.config = get_config()
        self._client = None  # created lazily only if API key is present
        self._prompt_template: str | None = None

    @property
    def _has_api_key(self) -> bool:
        return bool(self.config.ANTHROPIC_API_KEY)

    def _get_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.config.ANTHROPIC_API_KEY)
        return self._client

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

        if not self._has_api_key:
            logger.info(
                "requirement_extraction_offline_mode",
                tender_id=tender_id,
                reason="ANTHROPIC_API_KEY not set — using regex heuristics",
            )
            return self._extract_with_regex(tender_text, tender_id)

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
        message = self._get_client().messages.create(
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

    def _extract_with_regex(self, text: str, tender_id: str) -> list[Requirement]:
        """Heuristic regex-based extraction used when no API key is configured.

        Recognises the most common requirement patterns in Indian government
        tenders: turnover thresholds, experience requirements, ISO certifications,
        and net worth floors.  Coverage is intentionally narrow — this path
        exists only to make the pipeline runnable without credentials.
        Real extraction requires the LLM path.
        """
        requirements: list[Requirement] = []

        def _crore_value(val_str: str, unit: str) -> float:
            val = float(val_str.replace(",", ""))
            if "lakh" in unit.lower():
                val = val / 100
            return val

        def _find_clause(pos: int) -> str | None:
            snippet = text[max(0, pos - 200):pos]
            m = _CLAUSE_RE.search(snippet)
            return m.group(0) if m else None

        # --- Turnover ---
        for m in _TURNOVER_RE.finditer(text):
            val = _crore_value(m.group(1), m.group(2))
            requirements.append(Requirement(
                requirement_id=generate_id("req"),
                category="turnover",
                description=f"Average Annual Turnover not less than Rs. {val:.1f} Crore "
                            f"(last 3 financial years)",
                threshold_value=val,
                threshold_unit="INR_crores_annual_average",
                threshold_period_years=3,
                is_mandatory=True,
                source_clause=_find_clause(m.start()),
                raw_text=m.group(0),
            ))

        # --- Experience (project count + value) ---
        exp_matches = list(_EXPERIENCE_RE.finditer(text))
        val_matches = list(_EXPERIENCE_VALUE_RE.finditer(text))
        if exp_matches:
            count_str = exp_matches[0].group(2) or exp_matches[0].group(3) or "1"
            count = int(count_str) if count_str.isdigit() else 2
            proj_val = None
            if val_matches:
                proj_val = _crore_value(val_matches[0].group(1), val_matches[0].group(2))
            desc = (
                f"Successfully completed at least {count} similar works"
                + (f", each of value not less than Rs. {proj_val:.1f} Crore" if proj_val else "")
            )
            requirements.append(Requirement(
                requirement_id=generate_id("req"),
                category="experience",
                description=desc,
                threshold_value=proj_val,
                threshold_unit="INR_crores_per_project" if proj_val else None,
                is_mandatory=True,
                source_clause=_find_clause(exp_matches[0].start()),
                raw_text=exp_matches[0].group(0),
            ))

        # --- ISO Certifications ---
        seen_certs: set[str] = set()
        for m in _ISO_RE.finditer(text):
            cert = f"ISO {m.group(1)}"
            if cert in seen_certs:
                continue
            seen_certs.add(cert)
            requirements.append(Requirement(
                requirement_id=generate_id("req"),
                category="certification",
                description=f"Valid {cert} certification required",
                threshold_value=None,
                threshold_unit=None,
                is_mandatory=True,
                source_clause=_find_clause(m.start()),
                certification_name=cert,
                raw_text=m.group(0),
            ))

        # --- Net Worth ---
        for m in _NETWORTH_RE.finditer(text):
            val_str = m.group(1)
            unit_str = m.group(2)
            if not val_str:
                continue
            val = _crore_value(val_str, unit_str)
            requirements.append(Requirement(
                requirement_id=generate_id("req"),
                category="financial",
                description=f"Net Worth not less than Rs. {val:.1f} Crore",
                threshold_value=val,
                threshold_unit="INR_crores",
                is_mandatory=True,
                source_clause=_find_clause(m.start()),
                raw_text=m.group(0),
            ))

        logger.info(
            "requirement_extraction_regex_complete",
            tender_id=tender_id,
            requirements_found=len(requirements),
            note="Offline mode — LLM extraction disabled",
        )
        return requirements
