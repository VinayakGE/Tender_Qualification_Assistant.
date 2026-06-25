"""Application configuration loaded from environment / .env file."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Central configuration for the Tender Qualification Assistant.

    All values can be overridden via environment variables or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM
    ANTHROPIC_API_KEY: str = Field(..., description="Anthropic API key")
    MODEL: str = Field(
        default="claude-sonnet-4-6",
        description="Claude model to use for all LLM calls",
    )
    MAX_TOKENS: int = Field(
        default=4096,
        description="Maximum tokens for LLM responses",
    )

    # Directory paths
    INCOMING_DIR: Path = Field(
        default=Path("data/incoming"),
        description="Folder watcher monitors this directory for new PDFs",
    )
    RAW_DIR: Path = Field(
        default=Path("data/raw-tenders"),
        description="PDFs are moved here after processing",
    )
    PARSED_DIR: Path = Field(
        default=Path("data/parsed-tenders"),
        description="Extracted text and requirements saved here",
    )
    COMPANY_PROFILES_DIR: Path = Field(
        default=Path("data/company-profiles"),
        description="Company profile JSONs",
    )
    OUTCOMES_DIR: Path = Field(
        default=Path("data/outcomes"),
        description="Recommendation outputs saved here",
    )
    PROMPTS_DIR: Path = Field(
        default=Path("prompts"),
        description="Directory containing versioned prompt files",
    )

    # Ledger
    LEDGER_FILE: Path = Field(
        default=Path("decision-ledger.json"),
        description="Path to the append-only decision ledger JSON file",
    )

    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR",
    )
    LOG_FORMAT: str = Field(
        default="json",
        description="Log output format: 'json' or 'console'",
    )

    # Pipeline thresholds (can be tuned without code changes)
    QUALIFICATION_PASS_THRESHOLD: int = Field(
        default=80,
        description="Minimum qualification score for PASS (80+)",
    )
    QUALIFICATION_MARGINAL_THRESHOLD: int = Field(
        default=60,
        description="Minimum qualification score for MARGINAL (60-79)",
    )
    INCUMBENT_RISK_HIGH_THRESHOLD: int = Field(
        default=70,
        description="Incumbent risk score at or above which a BID is downgraded to REVIEW",
    )
    OCR_FALLBACK_CHARS_PER_PAGE: int = Field(
        default=100,
        description="Average characters per page below which OCR fallback is triggered",
    )


def get_config() -> Config:
    """Return a Config instance. Cached at module level for reuse."""
    return _config


# Module-level singleton
_config = Config()
