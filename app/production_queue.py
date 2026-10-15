"""Turn ranked candidates into approval-ready content plans."""

import json
from pathlib import Path
from typing import Any

from app.content_plan import build_content_plan

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "data" / "candidates.json"
QUEUE = ROOT / "data" / "approval_queue.json"


def build_queue(limit: int = 10) -> list[dict[str, Any]]:
    if not CANDIDATES.exists():
        return []

    ranked = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    queue: list[dict[str, Any]] = []

    for item in ranked[:limit]:
        candidate = item.get("candidate", {})
        plan = build_content_plan(candidate)
        queue.append(
            {
                "status": "pending_approval",
                "score": item.get("score", 0),
                "candidate": candidate,
                "content_plan": plan.to_dict(),
            }
        )

    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    return queue


if __name__ == "__main__":
    print(f"Prepared {len(build_queue())} items for approval")
