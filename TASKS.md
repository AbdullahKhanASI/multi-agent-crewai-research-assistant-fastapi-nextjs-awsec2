# TASKS: crewAI Multi‑Agent Research Application

A structured checklist of deliverables and tasks. Use this as the source of truth for progress tracking.

Legend: [x] completed, [ ] pending, [~] in progress

## Deliverable 0 — Bootstrap & Docs

- [x] Create backend and frontend folders
- [x] Initialize backend with `uv` and create `.venv`
- [x] Scaffold Next.js app in `frontend/` using `pnpm create next-app` (TS, App Router, Tailwind, ESLint)
- [x] Update `PLAN.md` with current structure and package managers
- [x] Add `RULES.md` with project structure and package manager usage

## Deliverable 1 — Backend Foundation (FastAPI)

- [x] Add `app.main` with FastAPI app and root health endpoint (`GET /healthz`)
- [x] Add `app.config` with Pydantic settings (env‑driven, `.env.example`)
- [x] Add CORS allowing `http://localhost:3000` in dev
- [x] Create router package (`app/routers`) and register under `/api/v1`
- [x] Define initial `tool.uv.scripts` in `pyproject.toml` (e.g., `serve`, `test`)
- [x] Add minimal tests scaffold (e.g., `tests/unit/test_health.py`)

## Deliverable 2 — CrewAI Orchestrator & Agents

- [x] Create `app/services/orchestrator.py` to construct crew (agents, tasks, tools)
- [x] Define agents with separate folders exposing FastAPI endpoints under `/api/v1/agents/*`
- [ ] Implement pluggable search tool (stub provider + interface)
- [ ] Add extraction helpers (`extractors/readability.py`, `pdf.py` stubs)
- [ ] Add data models in `app/schemas/research.py`

## Deliverable 3 — Research API Endpoints

- [x] `/api/v1/research/search` — optimize queries + list candidates
- [x] `/api/v1/research/gather` — evidence retrieval, SSE/streaming progress
- [x] `/api/v1/research/synthesize` — build report with inline citations
- [x] `/api/v1/research/title` — title and abstract generation
- [x] `/api/v1/research/review` — red‑team issues and fixes
- [x] `/api/v1/runs/{run_id}/download` — stream ZIP of artifacts (placeholder)
- [x] Streaming helpers (`services/streaming.py`) and storage (`services/storage.py`)

## Deliverable 4 — Frontend Foundation (Next.js)

- [x] Add base app layout and theme
- [x] Add API client (`src/lib/api.ts`) and shared types inline
 - [x] Add SSE hook (`src/hooks/useSSE.ts`) for streaming endpoints
- [x] Wire environment config (`.env.local.example`) and base URL

## Deliverable 5 — UX Flows

- [x] Home page — topic input + constraints (basic topic input)
- [ ] Sources — show optimized queries and candidate sources, approval UI
- [x] Gather — progress stream with evidence counts and excerpt previews (basic non-stream view)
 - [x] Draft — live synthesis stream (SSE) with basic rendering
- [ ] Review — issues list and apply fixes
- [ ] Export — download ZIP and copy Markdown

## Deliverable 6 — Quality & Testing

- [ ] Unit tests for services and schemas
- [ ] Integration tests for API routes
- [ ] Frontend component tests (critical flows)

## Deliverable 7 — Observability & Ops

- [ ] Request ID and logging middleware
- [ ] Optional OpenTelemetry wiring (config‑gated)
- [ ] Structured logs for long‑running tasks

## Deliverable 8 — DX & Scripts

- [ ] Add convenience scripts: `uv run serve`, `uv run test`, `pnpm dev`, `pnpm build`
- [ ] Document local dev workflows in `README.md` (root + per app)
- [ ] Provide `.env.example` for backend and frontend

## Deliverable 9 — Packaging & Deployment

- [ ] Backend Dockerfile + multi‑stage build
- [ ] Frontend Dockerfile + production build
- [ ] docker‑compose for local orchestration
- [ ] Production config notes (CORS, secrets, logging)

## Stretch — Persistence & Caching (Optional)

- [ ] Pluggable cache/vector store for recall
- [ ] Persist run metadata for session resume

---

Backlog items can be appended to the relevant deliverable as needed. Update statuses here as tasks progress.
