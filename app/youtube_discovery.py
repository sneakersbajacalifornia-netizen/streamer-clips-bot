"""YouTube discovery adapter.

Uses YouTube Data API search metadata when YOUTUBE_API_KEY is configured.
No video downloading is performed here.
"""

import os
from datetime import datetime, timezone
from typing import Iterable

from app.multi_source import Candidate, normalize_candidate


YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def discover_youtube_candidates(
    queries: Iterable[str],
    max_results_per_query: int = 10,
) -> list[Candidate]:
    """Search YouTube for recent streamer-related videos.

    This function is intentionally dependency-light. It returns an empty list
    when no API key is configured, allowing the rest of the pipeline to run.
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return []

    try:
        import urllib.parse
        import urllib.request
        import json

        results: list[Candidate] = []
        for query in queries:
            params = urllib.parse.urlencode(
                {
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "order": "date",
                    "maxResults": max(1, min(max_results_per_query, 50)),
                    "key": api_key,
                }
            )
            with urllib.request.urlopen(
                f"{YOUTUBE_API_BASE}/search?{params}", timeout=20
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))

            for item in payload.get("items", []):
                video_id = item.get("id", {}).get("videoId")
                snippet = item.get("snippet", {})
                if not video_id:
                    continue
                published = snippet.get("publishedAt")
                created = datetime.fromisoformat(
                    published.replace("Z", "+00:00")
                ) if published else datetime.now(timezone.utc)
                results.append(
                    normalize_candidate(
                        source="youtube",
                        source_id=video_id,
                        streamer=snippet.get("channelTitle", "unknown"),
                        title=snippet.get("title", ""),
                        url=f"https://www.youtube.com/watch?v={video_id}",
                        created_at=created,
                        metadata={
                            "description": snippet.get("description", ""),
                            "channel_id": snippet.get("channelId"),
                        },
                    )
                )
        return results
    except Exception:
        # Discovery must not take down the complete scheduled pipeline because
        # one external source is unavailable.
        return []
