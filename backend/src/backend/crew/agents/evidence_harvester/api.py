from __future__ import annotations

import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from ....app.services.fetch_extract import extract_from_url, evidence_from_text
from ....app.services.websearch import _domain

router = APIRouter(tags=["agent:evidence-harvester"], prefix="/agents/evidence-harvester")


class HarvestRequest(BaseModel):
    run_id: str | None = None
    sources: list[dict] = []


@router.post("/harvest")
async def harvest(req: HarvestRequest):
    run_id = req.run_id or uuid.uuid4().hex[:12]
    evidence = []
    for src in req.sources[:8]:
        url = src.get("url")
        if not url:
            continue
        extracted = extract_from_url(url)
        quotes = evidence_from_text(url, extracted.get("title", ""), extracted.get("text", ""), keywords=["flow", "productivity"], max_quotes=2)
        for ev in quotes:
            ev["publisher"] = _domain(url)
            evidence.append(ev)
    return {"run_id": run_id, "evidence": evidence}
