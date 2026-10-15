"""Viral scoring for clip candidates.

This is intentionally provider-agnostic: discovery providers can be added later.
"""

from .models import ClipCandidate


def viral_score(clip: ClipCandidate) -> float:
    """Return a 0-100 heuristic score based on available metadata."""
    views_score = min(45.0, clip.views / 1000.0)
    duration_score = 15.0 if clip.duration_seconds and 12 <= clip.duration_seconds <= 55 else 5.0
    freshness_score = 20.0 if clip.created_at else 0.0
    rights_score = 20.0 if clip.rights_status == "authorized" else 0.0
    return min(100.0, views_score + duration_score + freshness_score + rights_score)
