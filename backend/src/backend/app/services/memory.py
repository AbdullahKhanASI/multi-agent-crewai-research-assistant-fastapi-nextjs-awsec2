from __future__ import annotations

from typing import Dict, List

_EVIDENCE: Dict[str, List[dict]] = {}


def set_evidence(run_id: str, evidence: List[dict]) -> None:
    _EVIDENCE[run_id] = evidence


def get_evidence(run_id: str) -> List[dict]:
    return _EVIDENCE.get(run_id, [])

