"""Input validation utilities."""

import re
from typing import Any


def sanitize_text(text: str) -> str:
    """Basic text sanitization — strip control chars, limit length."""
    if not text:
        return ""
    # Remove control characters except newlines/tabs
    text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", text)
    # Limit length
    return text[:10000]


def validate_uuid(value: str) -> str | None:
    """Validate UUID format, return None if invalid."""
    if not value:
        return None
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    return value if uuid_pattern.match(value) else None


def validate_page(page: int | str, default: int = 1) -> int:
    """Validate page number."""
    try:
        p = int(page)
        return p if p >= 1 else default
    except (ValueError, TypeError):
        return default


def validate_limit(limit: int | str, default: int = 50, max_limit: int = 200) -> int:
    """Validate limit parameter."""
    try:
        l = int(limit)
        return min(max(l, 1), max_limit) if l >= 1 else default
    except (ValueError, TypeError):
        return default
