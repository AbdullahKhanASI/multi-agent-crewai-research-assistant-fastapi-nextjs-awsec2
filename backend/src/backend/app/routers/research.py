from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from ..services.orchestrator import Orchestrator
from ..services.memory import set_evidence, get_evidence
from ..services.streaming import sse_format
from fastapi.responses import StreamingResponse


router = APIRouter(tags=["research"], prefix="/research")


class SearchRequest(BaseModel):
    topic: str
    constraints: dict | None = None


@router.post("/search")
async def search(req: Request, payload: SearchRequest):
    orch = Orchestrator(req.app)
    return await orch.search(payload.topic, payload.constraints or {})


class GatherRequest(BaseModel):
    run_id: str | None = None
    sources: list[dict] | None = None


@router.post("/gather")
async def gather(req: Request, payload: GatherRequest):
    orch = Orchestrator(req.app)
    res = await orch.gather(payload.run_id, payload.sources or [])
    if res.get("run_id") and res.get("evidence") is not None:
        set_evidence(res["run_id"], res.get("evidence", []))
    return res


class SynthesizeRequest(BaseModel):
    run_id: str
    evidence: list[dict] | None = None


@router.post("/synthesize")
async def synthesize(req: Request, payload: SynthesizeRequest):
    orch = Orchestrator(req.app)
    return await orch.synthesize(payload.run_id, evidence=payload.evidence or [])


@router.get("/synthesize/stream")
async def synthesize_stream(req: Request, run_id: str):
    orch = Orchestrator(req.app)

    async def _gen():
        yield sse_format("progress", "Starting synthesis...")
        ev = get_evidence(run_id)
        yield sse_format("progress", f"Loaded {len(ev)} evidence items")
        data = await orch.synthesize(run_id, evidence=ev)
        import json

        yield sse_format("result", json.dumps(data))

    return StreamingResponse(_gen(), media_type="text/event-stream")


class TitleRequest(BaseModel):
    run_id: str


@router.post("/title")
async def title(req: Request, payload: TitleRequest):
    orch = Orchestrator(req.app)
    return await orch.title(payload.run_id)


class ReviewRequest(BaseModel):
    run_id: str


@router.post("/review")
async def review(req: Request, payload: ReviewRequest):
    orch = Orchestrator(req.app)
    return await orch.review(payload.run_id)
