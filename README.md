# Multi‑Agent Researcher

A full‑stack research assistant that orchestrates multiple lightweight agents to:

- Search the web for relevant sources
- Harvest evidence from pages
- Synthesize a structured summary
- Generate a title and abstract
- Review for gaps or issues

The backend is a FastAPI service using `uv` for dependency management. The frontend is a Next.js app. You can run them locally for development, or deploy both to a single EC2 instance behind Nginx.


## Repository Layout

- `backend/`: FastAPI app and agent endpoints
- `frontend/`: Next.js UI (Turbopack dev, production server via `next start`)
- `logs/`, `outputs/`: Local artifacts (optional)


## Prerequisites

- Git
- Backend: `uv` (Python manager) and a compatible Python toolchain (uv can install it)
- Frontend: Node.js 20+ and `pnpm` (or npm)

Helpful installs:

- Install uv (Linux/macOS):
  - `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Make sure uv is on your PATH (e.g., `~/.local/bin`)
- Install Node via nvm (recommended):
  - `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash`
  - `nvm install --lts` (Node 20+)
- Install pnpm (either):
  - `corepack enable && corepack prepare pnpm@latest --activate`
  - or `npm i -g pnpm`


## Quickstart: Local Development

1) Clone the repo

```bash
git clone https://github.com/<your-username>/multi-agent-crewai-researcher.git
cd multi-agent-crewai-researcher
```

2) Backend (FastAPI on http://localhost:8000)

```bash
cd backend
cp .env.example .env  # edit if you have API keys
# Optional: let uv install Python 3.12 toolchain for this project
uv python install 3.12
# Install deps into a local .venv
uv sync
# Run the API (reload for development)
uv run uvicorn backend.app.main:app --reload --port 8000
```

- Health check: `curl http://localhost:8000/healthz`
- Tests: `uv run pytest -q`

Environment notes:

- A working experience requires no keys (defaults use DuckDuckGo search and a heuristic synthesis fallback).
- For better results, provide keys in `backend/.env` (see `backend/.env.example`):
  - `SEARCH_PROVIDER=tavily` and `TAVILY_API_KEY=...`
  - `LLM_PROVIDER=openai` and `OPENAI_API_KEY=...`
  - Update CORS for dev if needed, e.g. `CORS_ORIGINS=["http://localhost:3000"]`

3) Frontend (Next.js on http://localhost:3000)

```bash
cd ../frontend
# Point the UI to the backend
printf "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000\n" > .env.local
pnpm install
pnpm dev
```

Open http://localhost:3000 and run a query. The app will:

- Search and list candidate sources
- Gather evidence
- Synthesize findings (SSE streaming supported)
- Generate a title/abstract and run a review
- Allow JSON or ZIP bundle download


## Configuration

- Backend env file: `backend/.env` (copy from `.env.example`)
  - `SEARCH_PROVIDER`: `tavily | bing | serpapi | ddg`
  - `LLM_PROVIDER`: `openai | azure-openai | anthropic | none`
  - Keys: `TAVILY_API_KEY`, `OPENAI_API_KEY`, etc.
  - `CORS_ORIGINS`: JSON array string of allowed origins (e.g., your frontend URL)
- Frontend env: `.env.local` for dev, `.env.production` for prod
  - `NEXT_PUBLIC_BACKEND_URL`: Base URL of the backend (no trailing slash), e.g. `http://localhost:8000` or `https://your-domain`


## Deploy: Single EC2 (Ubuntu) + Nginx

Below is a simple production setup for a single VM running both services, reverse‑proxied by Nginx. Adjust paths, usernames, and domains as needed.

1) Provision EC2

- AMI: Ubuntu 22.04 LTS (or similar)
- Security group: allow TCP 80 (HTTP) and 443 (HTTPS)

SSH to the instance:

```bash
ssh ubuntu@your-ec2-ip
```

2) Install dependencies

```bash
# uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# ensure ~/.local/bin on PATH in your shell profile, e.g. ~/.bashrc or ~/.zshrc

# Node + pnpm (via corepack)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo corepack enable && sudo corepack prepare pnpm@latest --activate

# Nginx
sudo apt-get update && sudo apt-get install -y nginx
```

3) Clone the project

```bash
cd /opt
sudo mkdir -p research
sudo chown $USER:$USER research
cd research
git clone https://github.com/<your-username>/multi-agent-crewai-researcher.git
cd multi-agent-crewai-researcher
```

4) Backend setup (service on 127.0.0.1:8000)

```bash
cd backend
cp .env.example .env
# Set production values in backend/.env, e.g.
#   ENVIRONMENT=production
#   CORS_ORIGINS=["https://your-domain"]
#   SEARCH_PROVIDER=tavily
#   TAVILY_API_KEY=... (optional but recommended)
#   LLM_PROVIDER=openai
#   OPENAI_API_KEY=... (optional but recommended)

~/.local/bin/uv python install 3.12
~/.local/bin/uv sync
```

Create a systemd unit for the backend:

```bash
sudo tee /etc/systemd/system/research-backend.service >/dev/null <<'SERVICE'
[Unit]
Description=Research Backend (FastAPI)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/research/multi-agent-crewai-researcher/backend
Environment=PATH=/home/ubuntu/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
Environment=ENVIRONMENT=production
# Loads variables from backend/.env automatically via pydantic-settings
ExecStart=/home/ubuntu/.local/bin/uv run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable --now research-backend
sudo systemctl status research-backend --no-pager
```

5) Frontend setup (service on 127.0.0.1:3000)

```bash
cd /opt/research/multi-agent-crewai-researcher/frontend
printf "NEXT_PUBLIC_BACKEND_URL=https://your-domain\n" > .env.production
pnpm install
pnpm build
```

Create a systemd unit for the frontend:

```bash
sudo tee /etc/systemd/system/research-frontend.service >/dev/null <<'SERVICE'
[Unit]
Description=Research Frontend (Next.js)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/research/multi-agent-crewai-researcher/frontend
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
Environment=NODE_ENV=production
Environment=PORT=3000
EnvironmentFile=-/opt/research/multi-agent-crewai-researcher/frontend/.env.production
ExecStart=/usr/bin/pnpm start -- -p 3000
Restart=on-failure

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable --now research-frontend
sudo systemctl status research-frontend --no-pager
```

6) Nginx reverse proxy

```bash
sudo tee /etc/nginx/sites-available/research >/dev/null <<'NGINX'
server {
    listen 80;
    server_name your-domain;

    # Frontend (Next.js)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_http_version 1.1;
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        # SSE streaming settings
        proxy_buffering off;
        proxy_read_timeout 3600s;
        add_header X-Accel-Buffering no;
    }

    # Optional: route backend healthcheck
    location = /healthz {
        proxy_pass http://127.0.0.1:8000/healthz;
    }
}
NGINX

sudo ln -s /etc/nginx/sites-available/research /etc/nginx/sites-enabled/research
sudo nginx -t && sudo systemctl reload nginx
```

(Optional) Enable HTTPS with Certbot:

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain
```

7) Verify

- Visit `https://your-domain`
- Backend: `curl -I http://127.0.0.1:8000/healthz` on the server
- Services: `systemctl status research-backend`, `systemctl status research-frontend`


## Troubleshooting

- CORS errors: ensure `backend/.env` has `CORS_ORIGINS=["https://your-domain"]` (or your local dev URL).
- SSE stalls behind Nginx: confirm `proxy_buffering off;` and long `proxy_read_timeout` under `/api/`.
- Frontend cannot reach backend: check `NEXT_PUBLIC_BACKEND_URL` and security group/firewall rules.
- uv not found in systemd: add `/home/ubuntu/.local/bin` to the service `PATH`.


## Useful Commands

- Backend dev: `cd backend && uv run uvicorn backend.app.main:app --reload --port 8000`
- Backend tests: `cd backend && uv run pytest -q`
- Frontend dev: `cd frontend && pnpm dev`
- Frontend build/start: `cd frontend && pnpm build && pnpm start`

