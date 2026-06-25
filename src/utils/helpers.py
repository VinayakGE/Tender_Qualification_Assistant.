"""Utility helper functions used across the pipeline."""

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def slugify(text: str) -> str:
    """Convert a string to a URL-safe slug.

    Lowercases the text, replaces non-alphanumeric characters with hyphens,
    and collapses multiple hyphens.

    Args:
        text: The input string.

    Returns:
        A lowercase, hyphen-separated slug.

    Example:
        >>> slugify("Tender for Supply of IT Equipment (2024)")
        'tender-for-supply-of-it-equipment-2024'
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def ensure_dir(path: Path | str) -> Path:
    """Create a directory and all parents if they do not exist.

    Args:
        path: Directory path to create.

    Returns:
        The Path object for the created directory.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_json(path: Path | str) -> Any:
    """Load and parse a JSON file.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed JSON content (dict, list, or scalar).

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Any, path: Path | str, indent: int = 2) -> Path:
    """Serialize data to a JSON file, creating parent directories as needed.

    Args:
        data: JSON-serializable data.
        path: Output file path.
        indent: JSON indentation level (default 2).

    Returns:
        The Path object for the written file.
    """
    p = Path(path)
    ensure_dir(p.parent)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
    return p


def now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string.

    Returns:
        UTC datetime in format "2024-06-15T10:23:44Z".
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_id(prefix: str = "") -> str:
    """Generate a short unique ID with an optional prefix.

    Args:
        prefix: Optional prefix string (e.g., "rec", "req", "ev").

    Returns:
        A prefixed UUID4 string (first 8 hex chars).

    Example:
        >>> generate_id("rec")
        'rec_a3f2b1c4'
    """
    uid = uuid.uuid4().hex[:8]
    return f"{prefix}_{uid}" if prefix else uid


def truncate_text(text: str, max_chars: int = 8000) -> str:
    """Truncate text to a maximum character length, appending an ellipsis.

    Used before sending large documents to the LLM to stay within context limits.

    Args:
        text: Input text.
        max_chars: Maximum number of characters to retain.

    Returns:
        Truncated text with "... [truncated]" appended if truncation occurred.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [truncated]"


def safe_avg(values: list[float | int]) -> float:
    """Compute the average of a list, returning 0.0 for an empty list.

    Args:
        values: List of numeric values.

    Returns:
        Average as a float, or 0.0 if the list is empty.
    """
    if not values:
        return 0.0
    return sum(values) / len(values)


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """Clamp a value between lo and hi.

    Args:
        value: The value to clamp.
        lo: Lower bound (default 0.0).
        hi: Upper bound (default 100.0).

    Returns:
        The clamped value.
    """
    return max(lo, min(hi, value))
