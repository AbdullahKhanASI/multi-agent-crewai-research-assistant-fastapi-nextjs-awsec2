from __future__ import annotations

from typing import Iterable

import httpx
from duckduckgo_search import DDGS
from tldextract import extract as tld_extract
from ..config import settings


def _domain(url: str) -> str:
    t = tld_extract(url)
    return ".".join([p for p in [t.domain, t.suffix] if p])


def search_candidates(queries: Iterable[str], max_results: int = 5) -> list[dict]:
    # Prefer Tavily if configured
    if settings.search_provider.lower() == "tavily" and settings.tavily_api_key:
        return _search_tavily(queries, max_results=max_results)
    # Fallback: DDG
    results: list[dict] = []
    seen: set[str] = set()
    with DDGS() as ddgs:
        for q in queries:
            for r in ddgs.text(q, region="us-en", safesearch="moderate", timelimit="y", max_results=max_results):
                url = r.get("href") or r.get("url")
                if not url or url in seen:
                    continue
                seen.add(url)
                results.append({
                    "url": url,
                    "title": r.get("title") or r.get("body") or "",
                    "publisher": _domain(url),
                    "date": r.get("date") or r.get("published") or "",
                    "score": 0.0,
                })
                if len(results) >= max_results:
                    break
            if len(results) >= max_results:
                break
    return results


def _search_tavily(queries: Iterable[str], max_results: int = 5) -> list[dict]:
    q = next(iter(queries))  # Use the first optimized query
    payload = {
        "api_key": settings.tavily_api_key,
        "query": q,
        "search_depth": "basic",
        "include_answer": False,
        "max_results": max_results,
    }
    results: list[dict] = []
    with httpx.Client(timeout=20) as client:
        resp = client.post("https://api.tavily.com/search", json=payload)
        resp.raise_for_status()
        data = resp.json()
        for r in data.get("results", [])[:max_results]:
            url = r.get("url")
            if not url:
                continue
            results.append({
                "url": url,
                "title": r.get("title") or "",
                "publisher": _domain(url),
                "date": r.get("published_date") or "",
                "score": r.get("score") or 0.0,
            })
    return results
