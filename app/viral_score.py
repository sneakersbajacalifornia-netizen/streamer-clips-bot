"""Ranking engine for short-form viral candidates."""

from dataclasses import dataclass
from datetime import datetime, timezone
import math


@dataclass
class ScoreBreakdown:
    total: float
    recency: float
    views: float
    duration: float
    source: float
    rights: float


def _hours_old(created_at: str) -> float:
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 3600)
    except (TypeError, ValueError):
        return 9999.0


def score_candidate(candidate) -> ScoreBreakdown:
    """Return a deterministic 0-100 score before expensive AI rendering."""
    age = _hours_old(candidate.created_at)

    # Recent material gets a strong advantage, with a gradual decay.
    recency = max(0.0, 30.0 * math.exp(-age / 24.0))

    # Log scaling prevents a huge creator from dominating purely on raw views.
    views = min(30.0, math.log10(max(1, candidate.views) + 1) * 4.0)

    # Shorts generally work best when the source moment is concise.
    if 12 <= candidate.duration_seconds <= 55:
        duration = 15.0
    elif 6 <= candidate.duration_seconds <= 75:
        duration = 10.0
    else:
        duration = 4.0

    source = 10.0 if candidate.source in {"twitch", "youtube"} else 6.0

    # Unknown is intentionally not treated as approved. A later rights gate
    # decides whether media can actually be rendered/published.
    rights = 15.0 if candidate.rights_status in {"authorized", "licensed"} else 0.0

    total = min(100.0, recency + views + duration + source + rights)
    return ScoreBreakdown(total, recency, views, duration, source, rights)


def rank_candidates(candidates, minimum_score: float = 35.0):
    ranked = []
    for candidate in candidates:
        breakdown = score_candidate(candidate)
        if breakdown.total >= minimum_score:
            ranked.append((breakdown.total, candidate))
    return sorted(ranked, key=lambda item: item[0], reverse=True)
