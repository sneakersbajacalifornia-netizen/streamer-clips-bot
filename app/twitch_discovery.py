"""Twitch Helix clip metadata discovery."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Iterable
from urllib.error import HTTPError, URLError

from app.multi_source import Candidate, normalize_candidate

HELIX = "https://api.twitch.tv/helix"
TOKEN_URL = "https://id.twitch.tv/oauth2/token"


def _get_json(url: str, headers: dict[str, str]) -> dict:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _token() -> str:
    client_id = os.getenv("TWITCH_CLIENT_ID", "")
    client_secret = os.getenv("TWITCH_CLIENT_SECRET", "")
    print(
        "Twitch credentials present: "
        f"client_id={'yes' if client_id else 'no'}, "
        f"client_secret={'yes' if client_secret else 'no'}"
    )
    if not client_id or not client_secret:
        print("Twitch token skipped: one or more credentials are missing")
        return ""
    params = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    })
    request = urllib.request.Request(
        f"{TOKEN_URL}?{params}",
        method="POST",
        headers={"Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            token = str(json.loads(response.read().decode("utf-8")).get("access_token", ""))
            print(f"Twitch token request: {'success' if token else 'empty token'}")
            return token
    except HTTPError as exc:
        print(f"Twitch token request failed: HTTP {exc.code}")
        return ""
    except URLError as exc:
        print(f"Twitch token request failed: network error ({exc.reason})")
        return ""
    except Exception as exc:
        print(f"Twitch token request failed: {type(exc).__name__}")
        return ""


def discover_twitch_clips(streamers: Iterable[str], limit_per_streamer: int = 25) -> list[Candidate]:
    token = _token()
    client_id = os.getenv("TWITCH_CLIENT_ID", "")
    if not token or not client_id:
        print("Twitch discovery stopped: no usable OAuth token")
        return []

    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    candidates: list[Candidate] = []

    for streamer in streamers:
        try:
            user_url = f"{HELIX}/users?login={urllib.parse.quote(streamer.strip().lower())}"
            users = _get_json(user_url, headers).get("data", [])
            if not users:
                print(f"Twitch streamer not found: {streamer}")
                continue
            broadcaster_id = users[0]["id"]
            params = urllib.parse.urlencode({
                "broadcaster_id": broadcaster_id,
                "first": min(limit_per_streamer, 100),
            })
            data = _get_json(f"{HELIX}/clips?{params}", headers).get("data", [])
            print(f"Twitch {streamer}: {len(data)} clips")
            for item in data:
                created = item.get("created_at") or datetime.now(timezone.utc).isoformat()
                candidates.append(
                    normalize_candidate(
                        source="twitch",
                        source_id=str(item.get("id", "")),
                        streamer=streamer,
                        title=str(item.get("title") or f"Clip de {streamer}"),
                        url=str(item.get("url", "")),
                        created_at=datetime.fromisoformat(created.replace("Z", "+00:00")),
                        views=int(item.get("view_count") or 0),
                        duration_seconds=int(float(item.get("duration") or 0)),
                        rights_status="unknown",
                        metadata={"creator_name": item.get("creator_name")},
                    )
                )
        except HTTPError as exc:
            print(f"Twitch {streamer}: HTTP {exc.code}")
        except URLError as exc:
            print(f"Twitch {streamer}: network error ({exc.reason})")
        except Exception as exc:
            print(f"Twitch {streamer}: {type(exc).__name__}")

    print(f"Twitch discovery total: {len(candidates)} clips")
    return candidates
