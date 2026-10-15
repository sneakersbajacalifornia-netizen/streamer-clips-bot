"""Scheduled discovery and viral-ranking entry point."""

import json
from pathlib import Path

from app.discovery import discover_clips
from app.multi_source import filter_usable_candidates, merge_candidates
from app.viral_score import rank_candidates
from app.youtube_discovery import discover_youtube_candidates

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "candidates.json"


def main() -> None:
    twitch_candidates = discover_clips()

    queries = [
        "AuronPlay clip", "Ibai clip", "Rubius clip", "IlloJuan clip",
        "JuanSGuarnizo clip", "ElMariana clip", "ElXokas clip",
        "WestCOL clip", "Spreen clip", "TheGrefg clip", "AriGameplays clip",
        "Knekro clip", "Rivers clip", "Peereira7 clip",
    ]
    youtube_candidates = discover_youtube_candidates(queries)

    candidates = filter_usable_candidates(
        merge_candidates(twitch_candidates, youtube_candidates)
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
    print(f"Ranked {len(payload)} candidates")


if __name__ == "__main__":
    main()
