# Project Rules and Usage

This repo contains a Python backend (uv-managed) and a Next.js frontend (pnpm-managed).

## Project Structure

```
.
├── PLAN.md
├── RULES.md
├── backend/
│   ├── .venv/
│   └── backend/
│       ├── .python-version
│       ├── README.md
│       ├── pyproject.toml
│       ├── src/
│       │   └── backend/
│       │       ├── __init__.py
│       │       ├── app/
│       │       │   ├── __init__.py
│       │       │   ├── config.py
│       │       │   ├── main.py
│       │       │   ├── routers/
│       │       │   │   ├── research.py
│       │       │   │   └── runs.py
│       │       │   └── services/
│       │       │       ├── orchestrator.py
│       │       │       ├── storage.py
│       │       │       └── streaming.py
│       │       └── crew/
│       │           └── agents/
│       │               ├── query_optimizer/{__init__.py,api.py}
│       │               ├── source_scout/{__init__.py,api.py}
│       │               ├── evidence_harvester/{__init__.py,api.py}
│       │               ├── citation_builder/{__init__.py,api.py}
│       │               ├── synthesizer/{__init__.py,api.py}
│       │               ├── title_abstract/{__init__.py,api.py}
│       │               └── reviewer/{__init__.py,api.py}
│       └── tests/
│           └── unit/
│               ├── test_health.py
│               └── test_research_flow.py
└── frontend/
    ├── package.json
    ├── pnpm-lock.yaml
    ├── next.config.ts
    ├── tsconfig.json
    ├── eslint.config.mjs
    ├── public/
    └── src/
```

## Package Managers

- Backend: `uv` (Python project & package manager)
- Frontend: `pnpm` (Node package manager)

## Backend (uv) Usage

- Enter the backend directory:
  - `cd backend`
- Create or recreate a virtual environment (already created as `.venv`):
  - `uv venv`
- Activate the environment (optional; you can also use `uv run`):
  - macOS/Linux: `source .venv/bin/activate`
  - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- Add dependencies (writes to `pyproject.toml` and updates lockfile):
  - `uv add <package>`
- Sync/install from lockfile and `pyproject.toml`:
  - `uv sync`
- Run commands from the package root (`backend`):
  - `uv run python -V`
  - Dev server: `uv run uvicorn backend.app.main:app --reload --port 8000`
  - Tests: `uv run pytest -q`

## Frontend (pnpm) Usage

- Enter the frontend directory:
  - `cd frontend`
- Install dependencies (already installed during scaffolding):
  - `pnpm install`
- Start the dev server:
  - `pnpm dev`
- Build for production:
  - `pnpm build`
- Add runtime dependency:
  - `pnpm add <package>`
- Add dev-only dependency:
  - `pnpm add -D <package>`

## Notes

- The uv project files are currently nested under `backend/backend/` (with `pyproject.toml` there). This mirrors how `uv init --package backend` scaffolds a package by default. We can flatten this to keep `pyproject.toml` at `backend/` later if preferred.
- Frontend was created with TypeScript, App Router, TailwindCSS, and ESLint using Next.js `create-next-app` (Next 15). Use `http://localhost:3000` in development.
