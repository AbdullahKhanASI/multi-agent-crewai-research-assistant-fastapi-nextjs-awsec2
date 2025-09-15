from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["agent:title-abstract"], prefix="/agents/title-abstract")


class TitleRequest(BaseModel):
    run_id: str


@router.post("/generate")
async def generate(req: TitleRequest):
    return {"run_id": req.run_id, "title": "Stubbed Research Title", "abstract": "A concise abstract of the research findings."}

