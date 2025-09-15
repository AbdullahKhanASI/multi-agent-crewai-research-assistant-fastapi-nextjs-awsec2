from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # backend/
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient  # type: ignore
from backend.app.main import app


def test_research_flow_endpoints():
    client = TestClient(app)

    # 1) search
    sr = client.post("/api/v1/research/search", json={"topic": "AI safety"})
    assert sr.status_code == 200
    sdata = sr.json()
    assert "optimized_queries" in sdata and isinstance(sdata["optimized_queries"], list)

    # 2) gather with dummy sources from source_scout stub
    candidates_resp = client.post(
        "/api/v1/agents/source-scout/discover", json={"queries": sdata["optimized_queries"]}
    )
    assert candidates_resp.status_code == 200
    candidates = candidates_resp.json()["candidates"]
    gr = client.post("/api/v1/research/gather", json={"sources": candidates})
    assert gr.status_code == 200
    gdata = gr.json()
    assert gdata.get("run_id")
    assert gdata.get("evidence_count") is not None

    run_id = gdata["run_id"]

    # 3) synthesize
    syn = client.post("/api/v1/research/synthesize", json={"run_id": run_id})
    assert syn.status_code == 200
    syn_data = syn.json()
    assert syn_data.get("run_id") == run_id
    assert isinstance(syn_data.get("sections"), list)

    # 4) title
    tr = client.post("/api/v1/research/title", json={"run_id": run_id})
    assert tr.status_code == 200
    tdata = tr.json()
    assert tdata.get("title")
    assert tdata.get("abstract")

    # 5) review
    rr = client.post("/api/v1/research/review", json={"run_id": run_id})
    assert rr.status_code == 200
    rdata = rr.json()
    assert isinstance(rdata.get("issues"), list)

