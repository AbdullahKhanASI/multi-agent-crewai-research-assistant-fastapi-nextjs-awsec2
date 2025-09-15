from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from urllib.parse import urlparse

router = APIRouter(tags=["agent:citation-builder"], prefix="/agents/citation-builder")


class BuildRequest(BaseModel):
    run_id: str
    evidence: list[dict]


@router.post("/build")
async def build(req: BuildRequest):
    citations = []
    seen = set()
    for i, e in enumerate(req.evidence):
        url = e.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        parsed = urlparse(url)
        citations.append({
            "id": f"C{i+1}",
            "url": url,
            "title": e.get("title") or parsed.netloc,
            "publisher": e.get("publisher") or parsed.netloc,
        })
    return {"run_id": req.run_id, "citations": citations}
