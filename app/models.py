from dataclasses import dataclass
from typing import Optional


@dataclass
class ClipCandidate:
    streamer: str
    source_url: str
    title: str
    created_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    views: int = 0
    score: float = 0.0
    rights_status: str = "unknown"
