from __future__ import annotations

from typing import Any, List

from ..config import settings

_HEADING_KEYS = {"heading", "title", "name", "label"}
_CONTENT_KEYS = {
    "content",
    "text",
    "summary",
    "finding",
    "insight",
    "value",
    "point",
    "statement",
    "details",
    "description",
    "body",
    "item",
    "bullet",
}


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
            except Exception:
                sections = _normalize_sections(None, text, evidence)
            else:
                sections = _normalize_sections(obj, text, evidence)
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
    bullets = _evidence_bullets(evidence)
    sections = [
        {"heading": "Executive Summary", "content": f"Built from {len(unique_sources)} sources."},
        {"heading": "Key Findings", "content": "\n".join(bullets) if bullets else "- No evidence extracted."},
    ]
    return {"run_id": run_id, "sections": sections, "quality_metrics": {"coverage": round(len(evidence) / max(1, len(unique_sources)), 2)}}


def _normalize_sections(obj: Any, raw_text: str, evidence: List[dict]) -> List[dict]:
    sections: List[dict] = []
    candidate_key_findings: Any = None

    if isinstance(obj, dict):
        if isinstance(obj.get("sections"), list):
            sections = _coerce_sections(obj["sections"])
        else:
            summary_text = None
            for key in ("executive_summary", "summary", "abstract", "overview", "tl_dr"):
                val = obj.get(key)
                if isinstance(val, str) and val.strip():
                    summary_text = val.strip()
                    break
            if summary_text:
                sections.append({"heading": "Executive Summary", "content": summary_text})

            for key in ("key_findings", "findings", "insights", "highlights", "key_points"):
                value = obj.get(key)
                if value:
                    candidate_key_findings = value
                    break

            # Some models return a dict mapping headings to content
            if not sections:
                maybe_sections = obj.get("sections")
                if isinstance(maybe_sections, dict):
                    for heading, content in maybe_sections.items():
                        if not content:
                            continue
                        sections.append({
                            "heading": heading.title() if isinstance(heading, str) else str(heading),
                            "content": content,
                        })

    elif isinstance(obj, list):
        sections = _coerce_sections(obj)

    if not sections and raw_text.strip():
        sections = [{"heading": "Findings", "content": raw_text.strip()}]

    if not sections:
        bullets = _evidence_bullets(evidence)
        if bullets:
            sections = [{"heading": "Key Findings", "content": "\n".join(bullets)}]

    _ensure_key_findings_section(sections, candidate_key_findings, evidence)

    return sections


def _coerce_sections(raw: Any) -> List[dict]:
    if not isinstance(raw, list):
        return []
    coerced: List[dict] = []
    for idx, item in enumerate(raw):
        heading = f"Section {idx + 1}"
        content: Any = item
        if isinstance(item, dict):
            heading = item.get("heading") or item.get("title") or item.get("name") or heading
            content = item.get("content")
            if content is None:
                for key in ("text", "body", "summary", "details", "value", "items", "bullets"):
                    if key in item and item[key] is not None:
                        content = item[key]
                        break
            if content is None:
                leftovers = {k: v for k, v in item.items() if k not in _HEADING_KEYS}
                content = leftovers if leftovers else None
            normalized_content = _prepare_section_content(content)
            if normalized_content is not None:
                content = normalized_content
        elif isinstance(item, str):
            content = item.strip()
        coerced.append({"heading": heading, "content": content})
    return coerced


def _normalize_key_findings_content(value: Any) -> Any:
    if isinstance(value, list):
        normalized: List[dict] = []
        for item in value:
            if isinstance(item, dict):
                entry = _coerce_dict_item(item)
                if entry:
                    normalized.append(entry)
            else:
                text = str(item).strip()
                if text:
                    normalized.append({"content": text})
        return normalized
    if isinstance(value, dict):
        normalized: List[dict] = []
        for heading, content in value.items():
            entry = _coerce_dict_item({"heading": heading, "content": content})
            if entry:
                normalized.append(entry)
        return normalized
    if isinstance(value, str):
        text = value.strip()
        return text if text else None
    return None


def _has_key_findings(sections: List[dict]) -> bool:
    for section in sections:
        heading = section.get("heading")
        if isinstance(heading, str) and heading.strip().lower() == "key findings" and section.get("content"):
            return True
    return False


def _ensure_key_findings_section(sections: List[dict], candidate: Any, evidence: List[dict]) -> None:
    if _has_key_findings(sections):
        return
    content = _normalize_key_findings_content(candidate) if candidate is not None else None
    if not content:
        bullets = _evidence_bullets(evidence)
        if bullets:
            content = "\n".join(bullets)
    if content:
        sections.append({"heading": "Key Findings", "content": content})


def _evidence_bullets(evidence: List[dict], limit: int = 5) -> List[str]:
    bullets: List[str] = []
    for i, e in enumerate(evidence[:limit], start=1):
        quote = (e.get("quote") or "").strip()
        if not quote:
            continue
        src = e.get("url") or ""
        bullets.append(f"- {quote} [{i}] ({src})".strip())
    return bullets


def _normalize_list_items(items: List[Any]) -> List[Any]:
    normalized: List[Any] = []
    for value in items:
        if isinstance(value, dict):
            entry = _coerce_dict_item(value)
            if entry:
                normalized.append(entry)
            continue
        text = str(value).strip()
        if text:
            normalized.append({"content": text})
    return normalized


def _prepare_section_content(content: Any) -> Any:
    if isinstance(content, list):
        normalized = _normalize_list_items(content)
        return normalized if normalized else None
    if isinstance(content, dict):
        entry = _coerce_dict_item(content)
        return entry.get("content") if entry else None
    if isinstance(content, str):
        text = content.strip()
        return text if text else None
    return content


def _coerce_dict_item(item: dict[str, Any]) -> dict[str, Any] | None:
    heading = None
    for key in _HEADING_KEYS:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            heading = value.strip()
            break

    content: Any = None
    for key in _CONTENT_KEYS:
        if key in item:
            content = item[key]
            break

    if content is None:
        leftovers = {k: v for k, v in item.items() if k not in _HEADING_KEYS.union(_CONTENT_KEYS)}
        if leftovers:
            parts = [f"{k}: {v}" for k, v in leftovers.items() if v is not None]
            content = "; ".join(parts) if parts else None

    if isinstance(content, list):
        content = _normalize_list_items(content)
    elif isinstance(content, dict):
        nested = _coerce_dict_item(content)
        content = nested.get("content") if nested else None
    elif isinstance(content, str):
        content = content.strip()

    if not content:
        return None

    entry: dict[str, Any] = {"content": content}
    if heading:
        entry["heading"] = heading
    return entry
