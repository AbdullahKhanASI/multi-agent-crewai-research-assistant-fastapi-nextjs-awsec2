from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from ....app.services.websearch import search_candidates

router = APIRouter(tags=["agent:source-scout"], prefix="/agents/source-scout")


class DiscoverRequest(BaseModel):
    queries: list[str]


@router.post("/discover")
async def discover(req: DiscoverRequest):
    cands = search_candidates(req.queries, max_results=5)
    return {"candidates": cands}
