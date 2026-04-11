"""Optional Tavily web search for trends (when USE_TAVILY_SEARCH is enabled)."""

import json
import os

import requests


def tavily_search_tool(query: str) -> str:
    """
    Run a live web search via Tavily. Requires TAVILY_API_KEY in the environment.
    Returns a compact text blob for the model (titles + snippets).
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return json.dumps(
            {"error": "TAVILY_API_KEY is not set; cannot run web search."}
        )

    resp = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": 6,
        },
        timeout=60,
    )
    resp.raise_for_status()
    payload = resp.json()
    results = payload.get("results") or []
    lines = []
    for r in results:
        title = r.get("title", "")
        content = (r.get("content") or "")[:500]
        url = r.get("url", "")
        lines.append(f"- {title}\n  {content}\n  {url}")
    return "\n".join(lines) if lines else "(no results)"
