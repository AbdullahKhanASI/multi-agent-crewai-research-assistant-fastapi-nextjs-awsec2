from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..services.storage import build_zip_bytes

router = APIRouter(tags=["runs"], prefix="/runs")


@router.get("/{run_id}/download")
async def download(run_id: str):
    # Placeholder implementation; later stream a ZIP archive
    return {"run_id": run_id, "status": "download-ready", "note": "ZIP streaming to be implemented"}


class BundleRequest(BaseModel):
    topic: str
    run_id: str | None = None
    optimized_queries: list[str] | None = None
    candidates: list[dict] | None = None
    evidence: list[dict] | None = None
    synthesis: dict | None = None
    title: dict | None = None
    review: dict | list | None = None
    generated_at: str | None = None


@router.post("/bundle")
async def bundle(req: BundleRequest):
    report = req.model_dump()
    data = build_zip_bytes(report)
    filename = f"research_{(req.topic or 'report').lower().replace(' ', '_')}.zip"
    return StreamingResponse(
        iter([data]),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
        },
    )
