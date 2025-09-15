from __future__ import annotations

from pathlib import Path
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
import json


def runs_dir() -> Path:
    base = Path(__file__).resolve().parents[4] / "storage" / "runs"
    base.mkdir(parents=True, exist_ok=True)
    return base


def run_path(run_id: str) -> Path:
    p = runs_dir() / run_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def _to_markdown(report: dict) -> str:
    lines: list[str] = []
    topic = report.get("topic")
    if topic:
        lines.append(f"# {topic}")
        lines.append("")
    title = report.get("title", {}) or {}
    if isinstance(title, dict) and title.get("title"):
        lines.append(f"## {title.get('title')}")
        if title.get("abstract"):
            lines.append("")
            lines.append(title.get("abstract"))
            lines.append("")
    synth = report.get("synthesis", {}) or {}
    sections = synth.get("sections") or []
    for s in sections:
        heading = s.get("heading") or "Section"
        content = s.get("content")
        lines.append(f"## {heading}")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and "heading" in item and "content" in item:
                    lines.append(f"- {item['heading']}: {item['content']}")
                else:
                    lines.append(f"- {json.dumps(item, ensure_ascii=False)}")
        elif isinstance(content, str):
            lines.append(content)
        else:
            lines.append(json.dumps(content, ensure_ascii=False, indent=2))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_zip_bytes(report: dict) -> bytes:
    """Build a ZIP archive (in-memory) for the given report dict."""
    buf = BytesIO()
    with ZipFile(buf, "w", compression=ZIP_DEFLATED) as z:
        # Full JSON report
        z.writestr("report.json", json.dumps(report, ensure_ascii=False, indent=2))
        # Markdown rendering
        z.writestr("report.md", _to_markdown(report))
        # Evidence JSONL
        evidence = report.get("evidence", []) or []
        ev_lines = "\n".join(json.dumps(e, ensure_ascii=False) for e in evidence)
        z.writestr("evidence.jsonl", ev_lines)
        # Candidates JSON
        cands = report.get("candidates", []) or []
        z.writestr("candidates.json", json.dumps(cands, ensure_ascii=False, indent=2))
        # Metadata
        meta = {
            "topic": report.get("topic"),
            "run_id": report.get("run_id"),
            "optimized_queries": report.get("optimized_queries"),
            "generated_at": report.get("generated_at"),
        }
        z.writestr("metadata.json", json.dumps(meta, ensure_ascii=False, indent=2))
    return buf.getvalue()
