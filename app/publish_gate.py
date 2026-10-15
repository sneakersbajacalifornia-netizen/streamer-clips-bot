"""Publish gate: only explicitly approved queue items may enter publishing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "approval_queue.json"


def approved_items() -> list[dict[str, Any]]:
    if not QUEUE.exists():
        return []
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    return [item for item in queue if item.get("status") == "approved"]


def mark_publishing(index: int) -> dict[str, Any]:
    items = approved_items()
    if index < 0 or index >= len(items):
        raise IndexError("Approved item does not exist")

    item = items[index]
    item["status"] = "publishing"
    item["publish_ready"] = True
    return item


def mark_published(item: dict[str, Any], video_id: str) -> dict[str, Any]:
    item = dict(item)
    item["status"] = "published"
    item["youtube_video_id"] = video_id
    return item
