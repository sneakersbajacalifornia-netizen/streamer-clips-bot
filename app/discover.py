"""CLI entry point for the first discovery stage."""

from __future__ import annotations

import json
from pathlib import Path

from twitch_client import discover_recent_clips

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "streamers.json"
OUTPUT = ROOT / "data" / "candidates.json"


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    clips = discover_recent_clips(config["streamers"], hours=24)
    clips.sort(key=lambda item: item.get("view_count", 0), reverse=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(clips, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Discovered {len(clips)} recent clips")


if __name__ == "__main__":
    main()
