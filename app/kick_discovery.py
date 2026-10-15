"""Kick clip metadata discovery.

Kick's documented public developer API currently focuses on channels,
livestreams and related resources; clip listing is not exposed there as a
stable public endpoint. This adapter therefore uses Kick's public website
clip listing endpoint as a best-effort metadata source only. It never bypasses
authentication or downloads media.

The endpoint can be overridden with KICK_CLIPS_ENDPOINT when Kick changes it.
If Kick blocks the GitHub Actions runner, the adapter safely returns no
candidates and the rest of the pipeline continues.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Iterable

from app.multi_source import Candidate, normalize_candidate

DEFAULT_ENDPOINT = "https://kick.com/api/v2/channels/{slug}/clips"

# Known aliases where a display name does not map cleanly to a Kick slug.
KICK_SLUGS = {
    "WestCOL": "westcol",
    "Davo Xeneize": "davoo",
    "La Cobra": "lacobra",
    "MrStivenTC": "mrstiventc",
    "AriGameplays": "arigameplays",
    "ElMariana": "elmariana",
    "ElXokas": "elxokas",
    "JuanSGuarnizo": "juansguarnizo",
    "Peereira7": "peereira7",
    "Spreen": "spreen",
    "TheGrefg": "thegrefg",
    "Knekro": "knekro",
    "Rivers": "rivers",
    "Willito": "willito",
}


def _slug_for(streamer: str) -> str:
    if streamer in KICK_SLUGS:
        return KICK_SLUGS[streamer]
    slug = streamer.strip().lower()
    slug = re.sub(r"[^a-z0-9_-]+", "", slug)
    return slug


def _as_int(value: object) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _as_duration(value: object) -> int:
    if isinstance(value, (int, float)):
        return max(0, int(value))
    if isinstance(value, str):
        parts = value.split(":")
        try:
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(float(parts[2]))
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(float(parts[1]))
            return int(float(value))
        except ValueError:
            return 0
    return 0


def _created_at(item: dict) -> datetime:
    for key in ("created_at", "createdAt", "date", "published_at"):
        value = item.get(key)
        if isinstance(value, str) and value:
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
            except ValueError:
                pass
    return datetime.now(timezone.utc)


def _items(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("data", "clips", "items", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
    return []


def discover_kick_clips(
    streamers: Iterable[str],
    limit_per_streamer: int = 25,
) -> list[Candidate]:
    """Return normalized Kick clip metadata for configured streamers."""
    endpoint_template = os.getenv("KICK_CLIPS_ENDPOINT", DEFAULT_ENDPOINT)
    user_agent = os.getenv(
        "KICK_USER_AGENT",
        "streamer-clips-bot/1.0 (metadata discovery; contact via repository)",
    )
    candidates: list[Candidate] = []

    for streamer in streamers:
        slug = _slug_for(streamer)
        if not slug:
            continue
        url = endpoint_template.format(slug=urllib.parse.quote(slug, safe=""))
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": user_agent,
                "Referer": f"https://kick.com/{slug}",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
            continue

        for item in _items(payload)[:limit_per_streamer]:
            clip_id = str(item.get("id") or item.get("uuid") or item.get("slug") or "")
            if not clip_id:
                continue
            clip_url = str(item.get("clip_url") or item.get("url") or f"https://kick.com/{slug}?clip={clip_id}")
            title = str(item.get("title") or item.get("name") or f"Clip de {streamer}")
            views = _as_int(item.get("views") or item.get("view_count") or item.get("views_count"))
            duration = _as_duration(item.get("duration") or item.get("duration_seconds"))
            candidates.append(
                normalize_candidate(
                    source="kick",
                    source_id=clip_id,
                    streamer=streamer,
                    title=title,
                    url=clip_url,
                    created_at=_created_at(item),
                    views=views,
                    duration_seconds=duration,
                    rights_status="unknown",
                    metadata={"kick_slug": slug},
                )
            )

    return candidates
