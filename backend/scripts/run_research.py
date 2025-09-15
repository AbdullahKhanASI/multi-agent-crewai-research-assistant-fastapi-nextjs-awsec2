from __future__ import annotations

import argparse
import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app


def run(topic: str) -> dict:
    client = TestClient(app)

    search_resp = client.post("/api/v1/research/search", json={"topic": topic})
    search_resp.raise_for_status()
    search_data = search_resp.json()

    candidates_resp = client.post(
        "/api/v1/agents/source-scout/discover",
        json={"queries": search_data.get("optimized_queries", [])},
    )
    candidates_resp.raise_for_status()
    candidates = candidates_resp.json().get("candidates", [])

    gather_resp = client.post(
        "/api/v1/research/gather",
        json={"sources": candidates},
    )
    gather_resp.raise_for_status()
    gather_data = gather_resp.json()
    run_id = gather_data.get("run_id")

    synth_resp = client.post(
        "/api/v1/research/synthesize",
        json={"run_id": run_id, "evidence": gather_data.get("evidence", [])},
    )
    synth_resp.raise_for_status()
    synth_data = synth_resp.json()

    title_resp = client.post("/api/v1/research/title", json={"run_id": run_id})
    title_resp.raise_for_status()
    title_data = title_resp.json()

    review_resp = client.post("/api/v1/research/review", json={"run_id": run_id})
    review_resp.raise_for_status()
    review_data = review_resp.json()

    return {
        "topic": topic,
        "optimized_queries": search_data.get("optimized_queries", []),
        "candidates": candidates,
        "run_id": run_id,
        "evidence_count": gather_data.get("evidence_count"),
        "synthesis": synth_data,
        "title": title_data,
        "review": review_data,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a research flow and save output JSON")
    parser.add_argument("--topic", default="Flow State for Productivity", help="Topic to research")
    parser.add_argument("--out", default="../outputs/research_output.json", help="Output JSON file path")
    args = parser.parse_args()

    result = run(args.topic)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(f"Saved research output to {out_path}")


if __name__ == "__main__":
    main()
