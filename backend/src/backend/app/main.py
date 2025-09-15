from __future__ import annotations

import asyncio
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import research, runs
from ..crew.agents.query_optimizer.api import router as query_optimizer_router
from ..crew.agents.source_scout.api import router as source_scout_router
from ..crew.agents.evidence_harvester.api import router as evidence_harvester_router
from ..crew.agents.citation_builder.api import router as citation_builder_router
from ..crew.agents.synthesizer.api import router as synthesizer_router
from ..crew.agents.title_abstract.api import router as title_abstract_router
from ..crew.agents.reviewer.api import router as reviewer_router


async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Place for starting background tasks or warmups
    yield
    # Graceful shutdown hooks can go here


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

# CORS for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


# Include agent routers under /api/v1/agents/*
app.include_router(query_optimizer_router, prefix=f"{settings.api_prefix}")
app.include_router(source_scout_router, prefix=f"{settings.api_prefix}")
app.include_router(evidence_harvester_router, prefix=f"{settings.api_prefix}")
app.include_router(citation_builder_router, prefix=f"{settings.api_prefix}")
app.include_router(synthesizer_router, prefix=f"{settings.api_prefix}")
app.include_router(title_abstract_router, prefix=f"{settings.api_prefix}")
app.include_router(reviewer_router, prefix=f"{settings.api_prefix}")

# Include app routers
app.include_router(research.router, prefix=f"{settings.api_prefix}")
app.include_router(runs.router, prefix=f"{settings.api_prefix}")


def cli() -> None:
    # Placeholder script entrypoint
    import asyncio

    async def _main():
        print("Backend app CLI - try: uv run uvicorn backend.app.main:app --reload")

    asyncio.run(_main())

