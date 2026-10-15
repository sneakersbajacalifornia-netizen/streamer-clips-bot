"""Approval state management for the mobile-friendly publishing gate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "approval_queue.json"

VALID_STATES = {"pending_approval", "approved", "rejected"}


def load_queue() -> list[dict[str, Any]]:
    if not QUEUE.exists():
        return []
    return json.loads(QUEUE.read_text(encoding="utf-8"))


def set_status(index: int, status: str) -> list[dict[str, Any]]:
    if status not in VALID_STATES:
        raise ValueError(f"Invalid status: {status}")

    queue = load_queue()
    if index < 0 or index >= len(queue):
        raise IndexError("Approval item does not exist")

    queue[index]["status"] = status
    QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    return queue


def pending_items() -> list[dict[str, Any]]:
    return [item for item in load_queue() if item.get("status") == "pending_approval"]
