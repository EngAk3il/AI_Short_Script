"""Web research for verified facts and source URLs."""
from __future__ import annotations

import json
import re
from typing import Any

from lib.reference_validator import check_url

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None  # type: ignore


TRUSTED_SUFFIXES = (
    "livemint.com",
    "economictimes.indiatimes.com",
    "moneycontrol.com",
    "thehindu.com",
    "indianexpress.com",
    "reuters.com",
    "bbc.com",
    "ndtv.com",
    "businesstoday.in",
    "hindustantimes.com",
)


def search_web(query: str, max_results: int = 10) -> list[dict[str, str]]:
    if DDGS is None:
        return []
    results: list[dict[str, str]] = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", r.get("link", "")),
                        "snippet": r.get("body", r.get("snippet", "")),
                    }
                )
    except Exception:
        return []
    return results


def gather_verified_sources(topic: str, max_sources: int = 6) -> list[dict[str, str]]:
    """Search and keep only URLs that respond OK."""
    queries = [
        f"{topic} India news",
        f"{topic} site:livemint.com OR site:economictimes.indiatimes.com",
    ]
    seen: set[str] = set()
    verified: list[dict[str, str]] = []

    for q in queries:
        for item in search_web(q, max_results=8):
            url = item.get("url", "").strip()
            if not url or url in seen:
                continue
            seen.add(url)
            check = check_url(url)
            if check.ok:
                item["verify_reason"] = check.reason
                verified.append(item)
            if len(verified) >= max_sources:
                return verified
    return verified


def sources_to_facts_block(sources: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "topic": "",
        "verified_sources": [
            {
                "title": s.get("title", ""),
                "url": s.get("url", ""),
                "snippet": s.get("snippet", ""),
            }
            for s in sources
        ],
        "instruction": (
            "Use ONLY these verified sources for statistics and claims. "
            "Every claim in the script must map to one of these URLs."
        ),
    }


def research_topic(topic: str, extra_facts: dict | None = None) -> dict[str, Any]:
    """Build facts dict from web search + optional user-provided facts file."""
    sources = gather_verified_sources(topic)
    facts: dict[str, Any] = sources_to_facts_block(sources)
    facts["topic"] = topic
    if extra_facts:
        facts["user_provided"] = extra_facts
        if extra_facts.get("verified_sources"):
            for s in extra_facts["verified_sources"]:
                url = s.get("url", "")
                if url and check_url(url).ok:
                    sources.append(s)
    facts["verified_sources"] = [
        {"title": s.get("title", ""), "url": s.get("url", ""), "snippet": s.get("snippet", "")}
        for s in sources
    ]
    return facts


def format_facts_for_prompt(facts: dict[str, Any]) -> str:
    return json.dumps(facts, indent=2, ensure_ascii=False)
