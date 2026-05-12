"""Serper.dev web-search tool with graceful no-key fallback.

Without `SERPER_API_KEY` set, the tool returns a clear "search disabled"
string rather than crashing — the template stays runnable on a fresh
laptop with only a Bedrock or Anthropic key.
"""
from __future__ import annotations

import os

import requests
from strands import tool

_SERPER_URL = "https://google.serper.dev/search"
_DEFAULT_TIMEOUT = 15


@tool
def serper_search(query: str, num_results: int = 5) -> str:
    """Search the live web via Serper.dev.

    Args:
        query: The search query.
        num_results: How many organic results to return (1-10).

    Returns:
        A formatted string with title, link, and snippet for each hit, or
        a short "search disabled" message if SERPER_API_KEY isn't set.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return (
            "[serper_search] SERPER_API_KEY not configured — web search is "
            "disabled. Use http_request to fetch a specific URL instead, "
            "or set SERPER_API_KEY in .env to enable live search."
        )

    num = max(1, min(int(num_results), 10))
    try:
        response = requests.post(
            _SERPER_URL,
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": num},
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return f"[serper_search] request failed: {exc}"

    payload = response.json()
    organic = payload.get("organic", [])
    if not organic:
        return f"[serper_search] no results for query: {query!r}"

    lines = [f"Top {len(organic)} results for {query!r}:\n"]
    for idx, hit in enumerate(organic[:num], start=1):
        lines.append(f"{idx}. {hit.get('title', '(no title)')}")
        lines.append(f"   {hit.get('link', '')}")
        snippet = hit.get("snippet", "").strip()
        if snippet:
            lines.append(f"   {snippet}")
        lines.append("")
    return "\n".join(lines).rstrip()
