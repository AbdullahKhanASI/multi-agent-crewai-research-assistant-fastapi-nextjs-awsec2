from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["agent:query-optimizer"], prefix="/agents/query-optimizer")


class OptimizeRequest(BaseModel):
    topic: str
    constraints: dict | None = None


@router.post("/optimize")
async def optimize(req: OptimizeRequest):
    topic = req.topic.strip()
    base = [topic]
    if req.constraints and isinstance(req.constraints, dict):
        if ds := req.constraints.get("date_start"):
            base.append(f"after:{ds}")
        if de := req.constraints.get("date_end"):
            base.append(f"before:{de}")
    # Simple heuristic expansion
    optimized = [" ".join(base), f"{topic} site:gov", f"{topic} filetype:pdf"]
    return {"optimized_queries": optimized}

