from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from backend.app.services.llm import _normalize_sections


def test_normalize_sections_handles_key_findings_list() -> None:
    data = {
        "summary": "Summary text",
        "key_findings": ["Finding one", "Finding two"],
    }
    evidence = [{"quote": "Quote A", "url": "https://example.com/a"}]

    sections = _normalize_sections(data, "Summary text", evidence)

    assert any(s.get("heading") == "Executive Summary" for s in sections)
    key_section = next(s for s in sections if s.get("heading") == "Key Findings")
    assert isinstance(key_section["content"], list)
    first_item = key_section["content"][0]
    assert isinstance(first_item, dict)
    assert first_item.get("content") == "Finding one"


def test_normalize_sections_coerces_section_list_items() -> None:
    raw = [
        {"title": "Executive Summary", "text": "Overview text"},
        {"heading": "Key Findings", "content": ["Point 1", "Point 2"]},
    ]
    evidence: list[dict] = []

    sections = _normalize_sections(raw, "", evidence)

    assert sections[0]["heading"] == "Executive Summary"
    key_section = sections[1]
    assert key_section["heading"] == "Key Findings"
    assert key_section["content"][0]["content"] == "Point 1"


def test_normalize_sections_handles_dict_items_in_list() -> None:
    raw = [
        {
            "heading": "Key Findings",
            "content": [
                {"finding": "Flow improves focus", "citation": "[1]"},
                {"finding": "Breaks sustain flow"},
            ],
        }
    ]

    sections = _normalize_sections(raw, "", [])

    key_section = sections[0]
    entries = key_section["content"]
    assert entries[0]["content"] == "Flow improves focus"
    assert entries[1]["content"] == "Breaks sustain flow"


def test_normalize_sections_builds_key_findings_from_evidence() -> None:
    payload = {"summary": "Only summary provided"}
    evidence = [
        {"quote": "Supported claim", "url": "https://example.com"},
    ]

    sections = _normalize_sections(payload, "Only summary provided", evidence)

    key_section = next(s for s in sections if s.get("heading") == "Key Findings")
    assert "Supported claim" in key_section["content"]
