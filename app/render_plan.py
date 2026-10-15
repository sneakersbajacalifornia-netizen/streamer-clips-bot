"""Build an FFmpeg rendering specification for approved/preview videos.

The renderer only consumes media that the acquisition layer has legitimately
obtained. It does not download or bypass source protections.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RenderPlan:
    input_path: str
    output_path: str
    width: int = 1080
    height: int = 1920
    fps: int = 30
    max_duration: int = 55
    subtitle_path: Optional[str] = None
    voice_path: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def build_render_plan(
    input_path: str,
    output_path: str,
    subtitle_path: Optional[str] = None,
    voice_path: Optional[str] = None,
) -> RenderPlan:
    """Return a safe default 9:16 plan for YouTube Shorts."""
    return RenderPlan(
        input_path=str(Path(input_path)),
        output_path=str(Path(output_path)),
        subtitle_path=str(Path(subtitle_path)) if subtitle_path else None,
        voice_path=str(Path(voice_path)) if voice_path else None,
    )


def ffmpeg_video_filter() -> str:
    """Center-crop landscape/square media into a 9:16 canvas."""
    return (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,setsar=1"
    )
