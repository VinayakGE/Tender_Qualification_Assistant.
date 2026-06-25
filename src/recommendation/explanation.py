"""LLM-powered natural language explanation generator for recommendations."""

import anthropic

from src.recommendation.engine import Recommendation
from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExplanationGenerator:
    """Generates a natural language explanation paragraph using Claude.

    Uses prompts/recommendation.md to produce a human-readable reasoning
    paragraph that explains the recommendation to a bid manager.
    """

    def __init__(self) -> None:
        self.config = get_config()
        self.client = anthropic.Anthropic(api_key=self.config.ANTHROPIC_API_KEY)
        self._prompt_template: str | None = None

    def generate(self, recommendation: Recommendation) -> str:
        """Generate a natural language explanation for a recommendation.

        Falls back to the structured reasoning string if LLM call fails.

        Args:
            recommendation: The Recommendation object to explain.

        Returns:
            A 3-5 sentence explanation paragraph.
        """
        try:
            prompt = self._build_prompt(recommendation)
            message = self.client.messages.create(
                model=self.config.MODEL,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            explanation = message.content[0].text.strip()
            logger.debug(
                "explanation_generated",
                recommendation_id=recommendation.recommendation_id,
                chars=len(explanation),
            )
            return explanation
        except Exception as exc:
            logger.warning(
                "explanation_generation_failed",
                recommendation_id=recommendation.recommendation_id,
                error=str(exc),
            )
            # Fallback to structured reasoning
            return recommendation.reasoning or self._fallback_explanation(recommendation)

    def _build_prompt(self, rec: Recommendation) -> str:
        """Build the explanation prompt from the template."""
        template = self._load_prompt_template()

        evidence_gaps_str = (
            "; ".join(rec.evidence_gaps[:5]) if rec.evidence_gaps else "None"
        )
        failed_reqs_str = (
            "; ".join(rec.failed_mandatory_requirements[:5])
            if rec.failed_mandatory_requirements
            else "None"
        )

        return (
            template
            .replace("{recommendation}", rec.recommendation)
            .replace("{qualification_score}", str(rec.qualification_score))
            .replace("{competitive_strength}", str(rec.competitive_strength or "N/A"))
            .replace("{incumbent_risk}", str(rec.incumbent_risk or "N/A"))
            .replace("{execution_risk}", str(rec.execution_risk or "N/A"))
            .replace("{value_score}", str(rec.value_score or "N/A"))
            .replace("{primary_bottleneck}", rec.primary_bottleneck or "None")
            .replace("{evidence_gaps}", evidence_gaps_str)
            .replace("{failed_mandatory_requirements}", failed_reqs_str)
            .replace("{confidence}", str(rec.confidence))
        )

    def _load_prompt_template(self) -> str:
        """Load and cache the recommendation prompt template."""
        if self._prompt_template is None:
            prompt_path = self.config.PROMPTS_DIR / "recommendation.md"
            if not prompt_path.exists():
                raise FileNotFoundError(f"Recommendation prompt not found: {prompt_path}")

            content = prompt_path.read_text(encoding="utf-8")

            # Extract the prompt block between triple-backtick markers
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

    def _fallback_explanation(self, rec: Recommendation) -> str:
        """Generate a simple fallback explanation without LLM."""
        parts = [f"Recommendation: {rec.recommendation}. Qualification score: {rec.qualification_score}/100."]
        if rec.primary_bottleneck:
            parts.append(f"Primary issue: {rec.primary_bottleneck}.")
        if rec.evidence_gaps:
            parts.append(f"Evidence gaps: {'; '.join(rec.evidence_gaps[:3])}.")
        return " ".join(parts)
