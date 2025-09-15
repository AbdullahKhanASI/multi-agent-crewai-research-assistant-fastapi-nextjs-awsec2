from __future__ import annotations

import hashlib
from typing import Any

import trafilatura


def extract_from_url(url: str) -> dict[str, Any]:
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return {"url": url, "title": "", "text": ""}
    # Trafilatura 2.x returns plain text; metadata extraction varies by version
    text = trafilatura.extract(downloaded, include_comments=False, include_formatting=False) or ""
    return {"url": url, "title": "", "text": text}


def split_sentences(text: str, limit: int = 2) -> list[str]:
    # Naive sentence split to avoid heavy deps
    sents = []
    for raw in text.replace("\n", " ").split(". "):
        s = raw.strip()
        if not s:
            continue
        if not s.endswith("."):
            s += "."
        sents.append(s)
        if len(sents) >= limit:
            break
    return sents


def evidence_from_text(url: str, title: str, text: str, keywords: list[str] | None = None, max_quotes: int = 3) -> list[dict]:
    if not text:
        return []
    quotes: list[str] = []
    if keywords:
        lowered = text.lower()
        for kw in keywords:
            idx = lowered.find(kw.lower())
            if idx != -1:
                start = max(0, idx - 160)
                end = min(len(text), idx + 240)
                excerpt = text[start:end].strip()
                quotes.append(excerpt)
                if len(quotes) >= max_quotes:
                    break
    # Fallback to first sentences
    if not quotes:
        quotes = split_sentences(text, limit=max_quotes)

    out: list[dict] = []
    for q in quotes:
        checksum = hashlib.sha256((url + q).encode("utf-8")).hexdigest()[:16]
        out.append({
            "url": url,
            "title": title,
            "quote": q,
            "selector": None,
            "checksum": checksum,
        })
    return out
