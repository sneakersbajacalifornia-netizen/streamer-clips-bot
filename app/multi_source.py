"""Multi-source candidate discovery.

This module normalizes discovery results from sources that expose public/searchable
metadata. It deliberately does not bypass access controls or download protected
media. Each adapter can be enabled independently as credentials become available.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Iterable, Optional


@dataclass
class Candidate:
    source: str
    source_id: str
    streamer: str
    title: str
    url: str
    created_at: str
    views: int = 0
    duration_seconds: int = 0
    rights_status: str = "unknown"
    metadata: Optional[dict] = None

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_candidate(
    source: str,
    source_id: str,
    streamer: str,
    title: str,
    url: str,
    created_at: Optional[datetime],
    views: int = 0,
    duration_seconds: int = 0,
    rights_status: str = "unknown",
    metadata: Optional[dict] = None,
) -> Candidate:
    """Create a normalized candidate used by the scoring pipeline."""
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return Candidate(
        source=source.lower().strip(),
        source_id=str(source_id),
        streamer=streamer.strip(),
        title=title.strip(),
        url=url.strip(),
        created_at=created_at.astimezone(timezone.utc).isoformat(),
        views=max(0, int(views)),
        duration_seconds=max(0, int(duration_seconds)),
        rights_status=rights_status.lower().strip(),
        metadata=metadata or {},
    )


def merge_candidates(*groups: Iterable[Candidate]) -> list[Candidate]:
    """Merge sources and remove exact duplicates by source + source_id."""
    merged: dict[tuple[str, str], Candidate] = {}
    for group in groups:
        for candidate in group:
            key = (candidate.source, candidate.source_id)
            merged[key] = candidate
    return list(merged.values())


def filter_usable_candidates(candidates: Iterable[Candidate]) -> list[Candidate]:
    """Keep candidates that are eligible for downstream review.

    Unknown rights are retained for manual/automated rights review; candidates
    explicitly marked blocked are removed before rendering.
    """
    return [c for c in candidates if c.rights_status != "blocked"]
