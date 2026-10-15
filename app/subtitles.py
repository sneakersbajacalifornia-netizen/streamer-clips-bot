"""Generate simple SRT subtitles from narration text.

This is a deterministic fallback. A later speech-to-text adapter can replace
it with word-level timestamps without changing the render interface.
"""

import re
from pathlib import Path


def _chunks(text: str, words_per_line: int = 7) -> list[str]:
    words = re.findall(r"\S+", text.strip())
    return [" ".join(words[i:i + words_per_line]) for i in range(0, len(words), words_per_line)]


def _timestamp(seconds: float) -> str:
    total_ms = max(0, int(seconds * 1000))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(text: str, output_path: str, total_seconds: float = 20.0) -> str:
    chunks = _chunks(text)
    if not chunks:
        raise ValueError("Narration text is empty")

    duration = max(0.8, total_seconds / len(chunks))
    lines = []
    for index, chunk in enumerate(chunks, 1):
        start = (index - 1) * duration
        end = min(total_seconds, index * duration)
        lines.extend([
            str(index),
            f"{_timestamp(start)} --> {_timestamp(end)}",
            chunk,
            "",
        ])

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)
