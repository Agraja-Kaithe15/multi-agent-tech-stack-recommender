"""Internal sunglasses catalog (static JSON) for the lab."""

import json
from pathlib import Path

_CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "catalog.json"


def product_catalog_tool() -> str:
    """Return the full product catalog as a JSON string for the LLM."""
    with open(_CATALOG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, indent=2)
