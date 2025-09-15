# PLAN: crewAI Multi‑Agent Research Application

> Production‑ready blueprint for a multi‑agent research system powered by **CrewAI** (Python) with a **FastAPI** backend and a **Next.js** (App Router) frontend. Project uses **uv** as the Python package & project manager.

---

## Project Setup Status

- Backend: created `backend/`, initialized with `uv` and a local virtual environment at `backend/.venv`. Project files were scaffolded under `backend/backend/` by `uv init` (current `pyproject.toml`: `backend/backend/pyproject.toml`).
- Frontend: created `frontend/` using `pnpm create next-app` (TypeScript, App Router, Tailwind, ESLint). Dependencies are installed and `pnpm-lock.yaml` is present.
- Package managers: Python uses `uv`; Node uses `pnpm`.

### Current Project Structure

```
.
├── PLAN.md
├── backend/
│   ├── .venv/
│   └── backend/
│       ├── .python-version
│       ├── README.md
│       ├── pyproject.toml
│       └── src/
│           └── backend/
│               ├── __init__.py
│               ├── app/
│               │   ├── __init__.py
│               │   ├── config.py
│               │   ├── main.py
│               │   ├── routers/
│               │   │   ├── research.py
│               │   │   └── runs.py
│               │   └── services/
│               │       ├── orchestrator.py
│               │       ├── storage.py
│               │       └── streaming.py
│               └── crew/
│                   └── agents/
│                       ├── query_optimizer/
│                       │   ├── __init__.py
│                       │   └── api.py
│                       ├── source_scout/
│                       │   ├── __init__.py
│                       │   └── api.py
│                       ├── evidence_harvester/
│                       │   ├── __init__.py
│                       │   └── api.py
│                       ├── citation_builder/
│                       │   ├── __init__.py
│                       │   └── api.py
│                       ├── synthesizer/
│                       │   ├── __init__.py
│                       │   └── api.py
│                       ├── title_abstract/
│                       │   ├── __init__.py
│                       │   └── api.py
│                       └── reviewer/
│                           ├── __init__.py
│                           └── api.py
└── frontend/
    ├── package.json
    ├── pnpm-lock.yaml
    ├── next.config.ts
    ├── tsconfig.json
    ├── eslint.config.mjs
    ├── public/
    └── src/
```

### Backend Tests Added

```
backend/
  backend/
    tests/
      unit/
        test_health.py
        test_research_flow.py
```

### Package Managers & Quick Usage

- uv (backend):
  - Create/activate env: `cd backend && uv venv` then `source .venv/bin/activate` (or use `uv run …`).
  - Add deps: `uv add fastapi` (writes to `pyproject.toml` and updates lockfile).
  - Install/sync: `uv sync`.
  - Run app (from `backend`): `uv run uvicorn backend.app.main:app --reload`.
  - Run tests (from `backend`): `uv run pytest -q`.
- pnpm (frontend):
  - Install deps: `cd frontend && pnpm install`.
  - Dev server: `pnpm dev`.
  - Add deps: `pnpm add <pkg>` (or `pnpm add -D <pkg>` for devOnly).

## 1) Goals & Non‑Goals

### Goals

- Accurate, traceable research summaries with **inline citations** and **downloadable evidence bundles**.
- Modular **multi‑agent crew** that divides research tasks (query optimization, source discovery, extraction, citation building, synthesis, titling, red‑teaming, etc.).
- **FastAPI** backend exposing REST endpoints (and streaming where useful) for: search, gather, synthesize, title, citations report, and artifact download.
- **Next.js** frontend that orchestrates workflows, displays streaming progress, and renders citations with per‑claim evidence.
- **uv‑managed** Python workspace for fast installs, reproducible builds (universal lockfile), and scriptable tasks.

### Non‑Goals (initial release)

- No authenticated multi‑tenant SaaS (single‑tenant dev preview).
- No paid integrations; only pluggable search providers (Tavily/Bing/SerpAPI) and public web scraping via configured tools.
- No long‑term user accounts; session‑scoped state only.

---

## 2) High‑Level Architecture

```
┌─────────────┐        HTTPS/JSON        ┌─────────────┐
│  Next.js    │  ─────────────────────▶  │   FastAPI   │
│  (App)      │   actions/hooks (SSE)    │  Backend    │
└─────┬───────┘                          └─────┬───────┘
      │                                     Crew Orchestrator
      │                             (CrewAI: Agents, Tasks, Tools)
      │                                           │
      │                                    ┌──────┴─────────┐
      │                                    │  Tool Layer    │
      │                                    │  (web search,  │
      │                                    │  scraping,     │
      │                                    │  readers, LLM) │
      │                                    └───┬───────┬────┘
      │                                        │       │
      │                                 Evidence store  │
      │                                 (tmp/objects)   │
      │                                        │       │
      │                               Cache / Vector DB │
      │                           (optional for recall) │
      ▼                                        ▼       ▼
Progress UI                          Artifacts (PDF, HTML, JSON)
```

- **CrewAI** coordinates agents and tasks; **FastAPI** exposes endpoints & streaming; **Next.js** renders progress and results.
- Artifacts (raw HTML snapshots, PDFs, extracted text, JSON citations) are materialized to `/backend/storage/…` and streamed as a ZIP on request.

---

## 3) Multi‑Agent Design (CrewAI)

Each agent owns a single responsibility and communicates via structured messages. Tools are injected per agent.

1. **Query Optimizer Agent**

   - **Goal:** Transform a user topic into precise, disambiguated queries with Boolean operators, synonyms, date constraints, and entity expansions.
   - **Inputs:** user topic + constraints (dates, domains, languages).
   - **Outputs:** ranked query list + rationale.

2. **Source Scout Agent**

   - **Goal:** Discover high‑quality candidate sources (news, papers, docs, official pages) and triage by authority, recency, and coverage.
   - **Tools:** web search API, domain/recency filters, robots‑aware fetch.
   - **Outputs:** source shortlist (URL, title, date, publisher, quality score).

3. **Evidence Harvester Agent**

   - **Goal:** Retrieve pages, extract main content, normalize (readability parse), and capture **verbatim excerpts** with stable anchors.
   - **Outputs:** `evidence.jsonl` with `{claim_stub, quote, url, date, selector/xpath, checksum}` and stored snapshots.

4. **Citation Builder Agent**

   - **Goal:** Convert excerpts into clean **citation entries** (APA/MLA or simple web style), deduplicate, and map citations to claims with offsets.
   - **Outputs:** `citations.json` + per‑claim mapping.

5. **Synthesizer Agent**

   - **Goal:** Draft a structured report (Executive Summary → Key Findings → Limitations) using only verified excerpts; insert inline citation markers.
   - **Guardrails:** refuses unsupported claims; requests more evidence when citation coverage < threshold.

6. **Title & Abstract Agent**

   - **Goal:** Generate SEO‑aware titles, concise abstracts, and slug suggestions consistent with report content.

7. **Red‑Team / Fact‑Check Agent**

   - **Goal:** Challenge the draft, flag weakly‑sourced statements, check date consistency, detect model leakage or hallucinations, and request remediation.

8. **Editorial QA Agent**

   - **Goal:** Enforce style guide (tone, reading level), section ordering, and citation formatting; ensure downloadable bundle integrity.

**Crew Orchestration**

- Define **Tasks** bound to **Agents**, set dependencies: `optimizer → scout → harvester → citations → synth → redteam → qa`.
- Provide **memory** for entity glossary and cross‑doc context (optional: vector store for re‑use between runs).
- Configure **tools** per agent (search, fetch, parser, metadata enricher).
- Set **completion criteria** (e.g., ≥ 3 high‑quality independent sources, ≤ 12h age for “breaking news” mode, ≥ 90% citation coverage).

---

## 4) Backend (FastAPI) — API Surface

### Endpoints (v1)

- `POST /api/v1/research/search` → run **optimizer + scout**; returns ranked queries & source shortlist. _(stream progress optional)_
- `POST /api/v1/research/gather` → run **harvester** on approved sources; returns evidence handles.
- `POST /api/v1/research/synthesize` → run **synthesizer**; returns structured report (JSON with sections + citation map). _(SSE/NDJSON stream of steps)_
- `POST /api/v1/research/title` → run **title & abstract**; returns title/abstract/slug.
- `POST /api/v1/research/review` → run **red‑team + QA**; returns issues & fixed draft.
- `GET  /api/v1/research/download/{run_id}` → stream a **ZIP**: report.md, citations.json, evidence.jsonl, snapshots/.
- `GET  /api/v1/runs/{run_id}` → status & artifacts manifest.

### Data Models (Pydantic)

- `SearchRequest`: topic, constraints (date_range, domains\[], language, freshness), mode.
- `SearchResponse`: optimized_queries\[], candidates\[].
- `GatherRequest`: run_id, sources\[].
- `EvidenceRecord`: url, title, publisher, date, quote, selector, checksum.
- `SynthesisResponse`: outline\[], sections\[], citations_map{claim_id→\[cit_id,…]}, quality_metrics.
- `TitleResponse`: title, abstract, slug.
- `ReviewResponse`: issues\[], severity, actions\[].

### Streaming

- For long‑running tasks, use **Server‑Sent Events** (text/event‑stream) or line‑delimited JSON from background coroutines.
- For downloads, use streaming responses backed by file iterators (no whole‑file memory load).

### Project Layout (Backend)

```
backend/
  pyproject.toml
  uv.lock
  src/
    app/
      __init__.py
      main.py              # FastAPI app, routers include
      config.py            # settings via pydantic-settings
      routers/
        research.py        # /api/v1/research/* endpoints
        runs.py            # /api/v1/runs/*
      services/
        orchestrator.py    # Crew creation, task graph
        storage.py         # artifact paths, ZIP stream
        streaming.py       # SSE helpers / generators
      crew/
        agents.py          # Agent definitions
        tools.py           # Search/fetch/parse tools
        tasks.py           # Task graph & dependencies
        prompts/
          *.md             # System & tool prompts per agent
      extractors/
        readability.py     # HTML→text
        pdf.py             # PDF parsing (if needed)
      schemas/
        research.py        # Pydantic models
      middleware/
        logging.py         # request IDs, tracing hooks
      telemetry/
        otel.py            # optional OpenTelemetry
  tests/
    unit/
    integration/
  storage/
    runs/{run_id}/...      # evidence & snapshots (gitignored)
  .env.example
```

### uv Configuration & Commands

- Initialize and lock:

  ```bash
  uv init --package backend
  uv add fastapi uvicorn crewai httpx pydantic pydantic-settings bs4 lxml readability-lxml python-dotenv
  uv add sse-starlette aiofiles tenacity typer --dev
  uv lock
  ```

- Run dev server:

  ```bash
  uv run uvicorn app.main:app --reload --port 8000
  ```

- Task scripts via `pyproject.toml` `tool.uv.scripts` (e.g., `serve`, `test`, `lint`).

### Key Implementation Notes

- **Routers** mounted under `/api/v1`.
- **CORS** allow `http://localhost:3000` in dev.
- **OpenAPI** auto‑docs at `/docs` & `/openapi.json`.
- **ZIP Streaming**: iterate over files in `/storage/runs/{run_id}` using chunked generator.

---

## 5) Frontend (Next.js — App Router, TypeScript)

### UI Flows

1. **Home** → Topic input + constraints.
2. **Sources** → Show optimized queries & candidate sources; user approves subset.
3. **Gather** → Progress stream + evidence counts; preview excerpts.
4. **Draft** → Live synthesis stream; inline citation markers clickable to reveal excerpt.
5. **Review** → Red‑team issues & fixes; accept changes.
6. **Export** → Download bundle (ZIP) or copy Markdown.

### Project Layout (Frontend)

```
frontend/
  package.json
  next.config.mjs
  tsconfig.json
  app/
    layout.tsx
    page.tsx                 # Home
    research/
      page.tsx               # Wizard wrapper
      sources/page.tsx
      gather/page.tsx
      draft/page.tsx
      review/page.tsx
      export/page.tsx
    api/                      # optional server actions
  src/
    components/
      QueryForm.tsx
      SourceList.tsx
      StreamLog.tsx
      DraftViewer.tsx
      CitationPopover.tsx
    hooks/
      useSSE.ts               # SSE client
    lib/
      api.ts                  # fetch helpers
      types.ts                # shared types (mirrors backend)
    styles/
      globals.css
  public/
    favicon.ico
  .env.local.example
```

### Integration Details

- **SSE client** for `/synthesize` & long tasks (fallback to polling).
- Render citations as footnotes and popovers showing verbatim excerpt + source metadata.
- Ensure linkable anchors per claim (deep‑link support).

---

## 6) CrewAI Implementation Sketch

```python
# src/app/crew/agents.py
from crewai import Agent

query_optimizer = Agent(
    name="Query Optimizer",
    role="Expand and refine research queries",
    goal=("Generate disambiguated, high‑recall/precision queries with"
          " boolean logic, synonyms, and date/domain filters."),
    tools=["web_search"],
    allow_delegation=False,
)

source_scout = Agent(
    name="Source Scout",
    role="Discover and rank credible sources",
    goal="Find authoritative, recent, diverse sources and score them.",
    tools=["web_search", "metadata_enricher"],
)

# ... evidence_harvester, citation_builder, synthesizer, title_agent,
# redteam, editorial_qa
```

```python
# src/app/crew/tasks.py
from crewai import Task
from .agents import (
    query_optimizer, source_scout, evidence_harvester,
    citation_builder, synthesizer, redteam, editorial_qa
)

optimize = Task(description="Optimize queries", agent=query_optimizer)
scout    = Task(description="Discover sources", agent=source_scout, depends_on=[optimize])
harvest  = Task(description="Extract evidence", agent=evidence_harvester, depends_on=[scout])
cites    = Task(description="Build citations", agent=citation_builder, depends_on=[harvest])
synth    = Task(description="Synthesize report", agent=synthesizer, depends_on=[cites])
rt       = Task(description="Red‑team checks", agent=redteam, depends_on=[synth])
qa       = Task(description="Editorial QA", agent=editorial_qa, depends_on=[rt])
```

```python
# src/app/services/orchestrator.py
from crewai import Crew
from .crew.tasks import optimize, scout, harvest, c.

crew = Crew(tasks=[optimize, scout, harvest, c, ...], verbose=True)
```

---

## 7) Data & Artifacts

- **Evidence**: JSONL with stable anchors (CSS selectors/XPath), page checksum, retrieval timestamp, normalized text, snippet offsets.
- **Citations**: Structured JSON (web style: author/site, title, publisher, date, url, access_date).
- **Report**: Markdown with inline markers like `[1]`, `[2]` mapped to `citations.json`.
- **Bundle**: ZIP tree

  ```
  report.md
  citations.json
  evidence.jsonl
  snapshots/
    0001.html
    0001.pdf (optional)
  manifest.json
  ```

---

## 8) Quality, Safety, and Guardrails

- **Citation Coverage Threshold**: refuse to publish when < 80% of claims are backed by excerpts.
- **Source Quality**: prefer primary sources, official docs, and recent content; penalize low‑credibility domains.
- **Date Discipline**: agents must surface explicit dates for time‑sensitive facts; red‑team verifies recency windows.
- **Attribution**: include per‑section bibliography and per‑claim footnotes.
- **PII/Robots**: respect `robots.txt`, avoid paywalled/private content unless user provides access.
- **Content Filters**: forbid unsafe categories as per policy.

---

## 9) Observability & Telemetry

- Request IDs in logs; per‑task timing and token counts.
- Optional **OpenTelemetry** traces for `/research/*` endpoints.
- **Run Manifest** saved with parameters, tool versions, and hashes for reproducibility.

---

## 10) Testing Strategy

- **Unit**: agent prompts/tools, parsers, citation formatting.
- **Integration**: end‑to‑end small topic run; asserts citation coverage and artifact integrity.
- **Contract**: frontend↔backend types (Zod on FE vs Pydantic JSON schema).
- **Load**: synthetic workload of concurrent runs; backpressure/queue sanity.

---

## 11) Security & Config

- **Secrets** via environment: search API keys, LLM keys.
- **CORS**: explicit origins.
- **Rate Limits** (reverse proxy or middleware).
- **Sandboxing**: limit network and file system writes to `/storage/runs`.

Example `.env.example` (backend)

```
OPENAI_API_KEY=
SEARCH_PROVIDER=tavily|bing|serpapi
SEARCH_API_KEY=
ALLOWED_ORIGINS=http://localhost:3000
```

---

## 12) Deployment

- **Local Dev**: `uv run uvicorn …` and `next dev`.
- **Docker**: multi‑stage images (uv cache layer for wheels).
- **Reverse Proxy**: Nginx or Vercel (FE) + fly.io/Render/EC2 (BE).
- **Static Export**: not applicable; App Router SSR recommended.

---

## 13) Roadmap (Phased)

1. **MVP**: search→gather→synthesize→download, manual source approval, single model provider.
2. **v0.2**: red‑team loop, editorial QA, quality metrics dashboard.
3. **v0.3**: persistent memory across runs (vector DB), dedupe cache, reranking.
4. **v0.4**: authentication, saved workspaces, org settings.
5. **v1.0**: multi‑tenant, billing, per‑domain plugins.

---

## 14) Example API Contracts

**POST** `/api/v1/research/search`

```json
{
  "topic": "Recent advances in retrieval‑augmented generation",
  "constraints": {
    "freshness_days": 90,
    "domains": ["arxiv.org", "openai.com"],
    "language": "en"
  },
  "mode": "balanced"
}
```

**200**

```json
{
  "optimized_queries": [
    "retrieval‑augmented generation survey 2024",
    "RAG evaluation benchmarks"
  ],
  "candidates": [
    {
      "url": "https://arxiv.org/...",
      "title": "A Survey on RAG",
      "publisher": "arXiv",
      "date": "2025‑05‑10",
      "score": 0.92
    },
    {
      "url": "https://openai.com/...",
      "title": "...",
      "publisher": "OpenAI",
      "date": "2025‑04‑21",
      "score": 0.81
    }
  ]
}
```

**GET** `/api/v1/research/download/{run_id}` → `application/zip` (streamed)

---

## 15) Developer Experience Checklist

- One‑command setup with **uv** (`uv sync`) and seed `.env` files.
- Type‑safe FE/BE contracts; shared `openapi.json` → `openapi‑typescript` for FE types.
- Lint/format: Ruff (Py), ESLint/Prettier (TS).
- Makefile (optional) proxying to uv & npm scripts.

---

## 16) References (add links in README)

- CrewAI: concepts (agents, tasks, crews), tools, flows.
- uv: project management, locking, scripts.
- FastAPI: path operations, custom/streaming responses, OpenAPI docs.
- Next.js: App Router & project structure.

---

**End of PLAN**
