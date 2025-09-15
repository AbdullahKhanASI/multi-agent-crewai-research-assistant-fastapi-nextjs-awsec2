from __future__ import annotations

from typing import List

from ..config import settings


def synthesize_with_llm(run_id: str, evidence: List[dict]) -> dict:
    if settings.llm_provider.lower() == "openai" and settings.openai_api_key:
        try:
            from openai import OpenAI
        except Exception:  # pragma: no cover
            return _fallback(run_id, evidence)

        client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url or None)
        quotes = []
        for i, e in enumerate(evidence[:10], start=1):
            src = e.get("url", "")
            quotes.append(f"[{i}] {e.get('quote','').strip()}\nSource: {src}")
        prompt = (
            "You are a research assistant. Given evidence quotes with sources, write a concise Executive Summary and 3-6 Key Findings, each grounded in the evidence (no hallucinations). "
            "Return JSON with keys: sections=[{heading, content}]."
            "\n\nEvidence:\n" + "\n\n".join(quotes)
        )
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a careful analyst. Only use provided evidence."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            content = completion.choices[0].message.content or ""
            # Try to coerce to JSON (handle ```json fenced blocks)
            import json
            text = content.strip()
            if text.startswith("```"):
                # Find first fenced block
                fence = "```"
                try:
                    start = text.index(fence) + len(fence)
                    # optional language tag
                    nl = text.find("\n", start)
                    payload = text[nl + 1 : text.rfind(fence)] if nl != -1 and text.rfind(fence) != -1 else text
                    text = payload.strip()
                except Exception:
                    pass
            try:
                obj = json.loads(text)
                sections = obj.get("sections", []) if isinstance(obj, dict) else []
                if not sections:
                    sections = [{"heading": "Findings", "content": content.strip()}]
            except Exception:
                sections = [{"heading": "Findings", "content": content.strip()}]
            return {"run_id": run_id, "sections": sections, "quality_metrics": {"coverage": round(len(evidence) / max(1, len(set(e.get('url') for e in evidence))), 2)}}
        except Exception:
            return _fallback(run_id, evidence)

    # Default fallback
    return _fallback(run_id, evidence)


def _fallback(run_id: str, evidence: List[dict]) -> dict:
    # Minimal heuristic fallback
    unique_sources = []
    seen = set()
    for e in evidence:
        u = e.get("url")
        if u and u not in seen:
            seen.add(u)
            unique_sources.append(u)
    bullets = []
    for i, e in enumerate(evidence[:5], start=1):
        bullets.append(f"- {e.get('quote','').strip()} [{i}] ({e.get('url','')})")
    sections = [
        {"heading": "Executive Summary", "content": f"Built from {len(unique_sources)} sources."},
        {"heading": "Key Findings", "content": "\n".join(bullets) if bullets else "- No evidence extracted."},
    ]
    return {"run_id": run_id, "sections": sections, "quality_metrics": {"coverage": round(len(evidence) / max(1, len(unique_sources)), 2)}}
