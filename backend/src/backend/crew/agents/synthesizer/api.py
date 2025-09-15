from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from ....app.services.websearch import _domain
from ....app.services.llm import synthesize_with_llm

router = APIRouter(tags=["agent:synthesizer"], prefix="/agents/synthesizer")


class SynthesizeRequest(BaseModel):
    run_id: str
    evidence: List[dict] | None = None


@router.post("/synthesize")
async def synthesize(req: SynthesizeRequest):
    ev = req.evidence or []
    return synthesize_with_llm(req.run_id, ev)
