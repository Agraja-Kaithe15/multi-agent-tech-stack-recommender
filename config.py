"""Central model IDs and feature flags (override via environment)."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load from the project directory (Streamlit's cwd is not always the repo root).
_PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(_PROJECT_ROOT / ".env")

GEMINI_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-3-flash-preview")
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image-preview")

USE_TAVILY_SEARCH = os.getenv("USE_TAVILY_SEARCH", "false").lower() in (
    "1",
    "true",
    "yes",
)


# Google AI Studio keys are typically 39 characters (prefix AIza…).
_EXPECTED_GEMINI_KEY_LEN = 39


def normalize_api_key(raw: str | None) -> str:
    if raw is None:
        return ""
    k = raw.strip().strip('"').strip("'")
    if k.startswith("\ufeff"):
        k = k.lstrip("\ufeff")
    return k


def resolve_google_api_key(sidebar_value: str | None = None) -> str:
    """
    Resolve API key for the Gemini Developer API (Google AI Studio).

    Order: sidebar, GOOGLE_API_KEY, GEMINI_API_KEY. Skips truncated `AIza…` keys
    so a bad `GOOGLE_API_KEY` does not block a valid `GEMINI_API_KEY`.
    """
    sources: list[tuple[str, str | None]] = [
        ("sidebar", sidebar_value),
        ("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY")),
        ("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY")),
    ]
    for _name, raw in sources:
        k = normalize_api_key(raw)
        if not k:
            continue
        if k.startswith("AIza") and len(k) < 38:
            continue
        return k
    return ""


def describe_api_key_problem(k: str) -> str | None:
    """Return a user-facing hint if the key is unlikely to work, else None."""
    if not k:
        return None
    if k.startswith("AIza") and len(k) < _EXPECTED_GEMINI_KEY_LEN:
        return (
            f"This key looks too short ({len(k)} characters). "
            f"Keys from Google AI Studio are usually {_EXPECTED_GEMINI_KEY_LEN} characters. "
            "Re-copy the full key from https://aistudio.google.com/apikey — "
            "ensure nothing is cut off at the start or end. "
            "If you use both GOOGLE_API_KEY and GEMINI_API_KEY in `.env`, remove or fix the bad one "
            "(GOOGLE_API_KEY is checked first)."
        )
    return None


def hint_if_only_truncated_keys_in_env() -> str | None:
    """When resolve returns empty, explain if .env clearly has a truncated AIza key."""
    for label, raw in (
        ("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY")),
        ("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY")),
    ):
        k = normalize_api_key(raw)
        if k.startswith("AIza") and len(k) < 38:
            return (
                f"`{label}` in `.env` looks like a truncated Gemini key "
                f"({len(k)} characters; full keys are usually {_EXPECTED_GEMINI_KEY_LEN}). "
                "Paste the complete key from https://aistudio.google.com/apikey "
                "or remove that line so the other variable can be used."
            )
    return None
