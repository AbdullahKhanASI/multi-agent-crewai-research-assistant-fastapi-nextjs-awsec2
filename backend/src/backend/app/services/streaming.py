from __future__ import annotations

from typing import AsyncIterator, Iterable


async def ldj_stream(items: list[dict]) -> AsyncIterator[str]:
    for obj in items:
        yield f"{obj}\n"


def sse_format(event: str | None, data: str) -> str:
    parts = []
    if event:
        parts.append(f"event: {event}")
    for line in data.splitlines() or [""]:
        parts.append(f"data: {line}")
    parts.append("")
    return "\n".join(parts) + "\n"

async def sse_progress(messages: Iterable[str]) -> AsyncIterator[str]:
    for m in messages:
        yield sse_format("progress", m)
