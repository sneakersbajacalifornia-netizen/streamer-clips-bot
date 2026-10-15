"""FFmpeg helpers for rendering approved/authorized media as vertical Shorts."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

WIDTH = 1080
HEIGHT = 1920
FPS = 30


def build_render_command(input_video: str | Path, output_video: str | Path, *, voice_audio: Optional[str | Path] = None, subtitles: Optional[str | Path] = None) -> list[str]:
    filters = [
        "scale=1080:1920:force_original_aspect_ratio=increase",
        "crop=1080:1920",
        "fps=30",
    ]
    if subtitles:
        subtitle_path = str(subtitles).replace("\\", "/").replace(":", "\\:")
        filters.append(f"subtitles='{subtitle_path}'")

    cmd = ["ffmpeg", "-y", "-i", str(input_video)]
    if voice_audio:
        cmd += ["-i", str(voice_audio)]

    cmd += [
        "-vf", ",".join(filters),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "21",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-movflags", "+faststart",
    ]

    if voice_audio:
        cmd += ["-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    else:
        cmd += ["-map", "0:v:0", "-c:a", "aac", "-b:a", "160k"]

    cmd.append(str(output_video))
    return cmd


def render_short(input_video: str | Path, output_video: str | Path, *, voice_audio: Optional[str | Path] = None, subtitles: Optional[str | Path] = None) -> Path:
    output = Path(output_video)
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(build_render_command(input_video, output, voice_audio=voice_audio, subtitles=subtitles), check=True)
    return output
