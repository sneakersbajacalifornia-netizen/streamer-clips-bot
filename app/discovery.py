"""Clip discovery interface.

Provider implementations will be connected here. No downloader is included by
this skeleton; sources must be used according to their APIs, terms and rights.
"""

from typing import Iterable
from .models import ClipCandidate


def discover_candidates(streamers: Iterable[str]) -> list[ClipCandidate]:
    """Return discovered candidates.

    Currently a placeholder. The production implementation will call approved
    discovery APIs and normalize their metadata into ClipCandidate objects.
    """
    return []
