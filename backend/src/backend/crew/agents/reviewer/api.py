from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["agent:reviewer"], prefix="/agents/reviewer")


class ReviewRequest(BaseModel):
    run_id: str


@router.post("/review")
async def review(req: ReviewRequest):
    return {"run_id": req.run_id, "issues": [{"message": "Check citation coverage", "severity": "info"}]}

