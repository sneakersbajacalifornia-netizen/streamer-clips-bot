"""Scheduled discovery entry point."""

import json
import os
from pathlib import Path

from app.discovery import discover_clips
from app.multi_source import filter_usable_candidates, merge_candidates
from app.youtube_discovery import discover_youtube_candidates


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "candidates.json"


def main() -> None:
    # Twitch discovery is provided by the existing adapter. If credentials are
    # not configured, it safely returns no candidates.
    twitch_candidates = discover_clips()

    queries = [
        "AuronPlay clip",
        "Ibai clip",
        "Rubius clip",
        "IlloJuan clip",
        "JuanSGuarnizo clip",
        "ElMariana clip",
        "ElXokas clip",
        "WestCOL clip",
        "Spreen clip",
    ]
    youtube_candidates = discover_youtube_candidates(queries)

    candidates = filter_usable_candidates(
        merge_candidates(twitch_candidates, youtube_candidates)
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps([c.to_dict() for c in candidates], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Discovered {len(candidates)} candidates")


if __name__ == "__main__":
    main()
