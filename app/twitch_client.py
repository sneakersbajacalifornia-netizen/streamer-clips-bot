"""Minimal Twitch Helix client for clip discovery.

This module only discovers clip metadata. Downloading third-party clips is
intentionally separate because Twitch's clip-download endpoint requires the
appropriate broadcaster/editor authorization.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
API_URL = "https://api.twitch.tv/helix"


class TwitchClient:
    def __init__(self, client_id: str | None = None, client_secret: str | None = None):
        self.client_id = client_id or os.environ["TWITCH_CLIENT_ID"]
        self.client_secret = client_secret or os.environ["TWITCH_CLIENT_SECRET"]
        self.session = requests.Session()
        self._token: str | None = None

    def app_token(self) -> str:
        response = self.session.post(
            TOKEN_URL,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            },
            timeout=30,
        )
        response.raise_for_status()
        self._token = response.json()["access_token"]
        return self._token

    def _headers(self) -> dict[str, str]:
        if not self._token:
            self.app_token()
        return {
            "Authorization": f"Bearer {self._token}",
            "Client-Id": self.client_id,
        }

    def users_by_login(self, logins: list[str]) -> list[dict[str, Any]]:
        params = [("login", login) for login in logins]
        response = self.session.get(
            f"{API_URL}/users", params=params, headers=self._headers(), timeout=30
        )
        response.raise_for_status()
        return response.json().get("data", [])

    def recent_clips(
        self,
        broadcaster_id: str,
        hours: int = 24,
        first: int = 100,
    ) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        started_at = now - timedelta(hours=hours)
        params = {
            "broadcaster_id": broadcaster_id,
            "started_at": started_at.isoformat().replace("+00:00", "Z"),
            "ended_at": now.isoformat().replace("+00:00", "Z"),
            "first": min(max(first, 1), 100),
        }
        response = self.session.get(
            f"{API_URL}/clips", params=params, headers=self._headers(), timeout=30
        )
        response.raise_for_status()
        return response.json().get("data", [])


def discover_recent_clips(streamers: list[str], hours: int = 24) -> list[dict[str, Any]]:
    client = TwitchClient()
    users = client.users_by_login(streamers)
    clips: list[dict[str, Any]] = []
    for user in users:
        for clip in client.recent_clips(user["id"], hours=hours):
            clips.append(clip)
    return clips
