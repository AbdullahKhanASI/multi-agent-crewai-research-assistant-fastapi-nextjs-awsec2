from __future__ import annotations

from typing import Any

import httpx
from fastapi import FastAPI
from httpx import ASGITransport


class Orchestrator:
    def __init__(self, app: FastAPI):
        self._app = app
        self._client = httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://orchestrator")

    async def search(self, topic: str, constraints: dict[str, Any]) -> dict[str, Any]:
        # Call Query Optimizer then Source Scout
        q = await self._post("/api/v1/agents/query-optimizer/optimize", json={"topic": topic, "constraints": constraints})
        candidates = await self._post("/api/v1/agents/source-scout/discover", json={"queries": q["optimized_queries"]})
        return {"optimized_queries": q["optimized_queries"], "candidates": candidates["candidates"]}

    async def gather(self, run_id: str | None, sources: list[dict]) -> dict[str, Any]:
        payload = {"run_id": run_id, "sources": sources}
        ev = await self._post("/api/v1/agents/evidence-harvester/harvest", json=payload)
        return {"run_id": ev.get("run_id"), "evidence": ev.get("evidence", []), "evidence_count": len(ev.get("evidence", []))}

    async def synthesize(self, run_id: str, evidence: list[dict] | None = None) -> dict[str, Any]:
        data = await self._post("/api/v1/agents/synthesizer/synthesize", json={"run_id": run_id, "evidence": evidence or []})
        return data

    async def title(self, run_id: str) -> dict[str, Any]:
        data = await self._post("/api/v1/agents/title-abstract/generate", json={"run_id": run_id})
        return data

    async def review(self, run_id: str) -> dict[str, Any]:
        data = await self._post("/api/v1/agents/reviewer/review", json={"run_id": run_id})
        return data

    async def _post(self, path: str, json: dict) -> dict[str, Any]:
        resp = await self._client.post(path, json=json)
        resp.raise_for_status()
        return resp.json()
