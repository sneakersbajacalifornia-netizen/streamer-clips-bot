"""YouTube upload adapter.

Credentials are supplied through GitHub Actions secrets. No OAuth tokens are
stored in source control.
"""

from __future__ import annotations

import os
from pathlib import Path


def upload_video(video_path: str | Path, title: str, description: str, publish_at: str | None = None) -> str:
    """Upload a video using a preconfigured YouTube OAuth refresh token.

    The actual network upload is intentionally guarded until credentials are
    configured and the approval/render pipeline has been tested end-to-end.
    """
    required = ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError("Missing YouTube credentials: " + ", ".join(missing))
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(path)
    raise NotImplementedError("YouTube upload is gated until the production test is explicitly enabled.")
