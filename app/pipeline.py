"""Scheduled multi-source discovery and viral-ranking entry point."""

from __future__ import annotations

import json
from pathlib import Path

from app.kick_discovery import discover_kick_clips
from app.multi_source import filter_usable_candidates, merge_candidates
from app.twitch_discovery import discover_twitch_clips
from app.viral_score import rank_candidates
from app.youtube_discovery import discover_youtube_candidates

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "streamers.json"
OUTPUT = ROOT / "data" / "candidates.json"


def load_streamers() -> list[str]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    return [str(name) for name in data.get("streamers", []) if str(name).strip()]


def main() -> None:
    streamers = load_streamers()

    twitch_candidates = discover_twitch_clips(streamers)
    kick_candidates = discover_kick_clips(streamers)
    queries = [f"{name} clip" for name in streamers]
    youtube_candidates = discover_youtube_candidates(queries)

    candidates = filter_usable_candidates(
        merge_candidates(twitch_candidates, kick_candidates, youtube_candidates)
    )
    ranked = rank_candidates(candidates)

    payload = [
        {"score": round(score, 2), "candidate": candidate.to_dict()}
        for score, candidate in ranked[:100]
    ]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"Ranked {len(payload)} candidates from "
        f"Twitch={len(twitch_candidates)}, "
        f"Kick={len(kick_candidates)}, "
        f"YouTube={len(youtube_candidates)}"
    )


if __name__ == "__main__":
    main()
