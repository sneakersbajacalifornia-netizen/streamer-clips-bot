"""Text-to-speech adapter for Shorts narration.

The pipeline keeps TTS behind a small interface so the voice provider can be
changed without changing discovery, scoring, approval, or rendering.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def build_tts_command(text: str, output_audio: str | Path) -> list[str]:
    """Build a local espeak-ng command for a zero-cost fallback voice."""
    output = str(output_audio)
    voice = os.getenv("TTS_VOICE", "es")
    speed = os.getenv("TTS_SPEED", "165")
    return [
        "espeak-ng",
        "-v", voice,
        "-s", speed,
        "-w", output,
        text,
    ]


def synthesize(text: str, output_audio: str | Path) -> Path:
    """Generate WAV narration using the local fallback TTS engine."""
    if not text.strip():
        raise ValueError("TTS text cannot be empty")
    output = Path(output_audio)
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(build_tts_command(text, output), check=True)
    return output
