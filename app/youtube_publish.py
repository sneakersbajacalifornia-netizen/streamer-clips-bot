"""YouTube publishing adapter.

Only approved, already-rendered videos should call this module.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _credentials() -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
        token_uri=os.environ["GOOGLE_TOKEN_URI"],
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def upload_short(video_path: str | Path, *, title: str, description: str,
                 publish_at: str | None = None,
                 privacy_status: str = "private") -> dict[str, Any]:
    """Upload a Short and optionally schedule publication."""
    if privacy_status not in {"private", "public", "unlisted"}:
        raise ValueError("Invalid privacy status")

    youtube = build("youtube", "v3", credentials=_credentials())
    status: dict[str, Any] = {"privacyStatus": privacy_status}

    if publish_at:
        dt = datetime.fromisoformat(publish_at.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        status = {
            "privacyStatus": "private",
            "publishAt": dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "categoryId": "24",
        },
        "status": status,
    }

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True),
    )
    return request.execute()
