"""Create a production-ready plan for a viral Short.

This module is intentionally provider-neutral: it creates the structure and
metadata first, so an LLM/TTS/rendering provider can be plugged in later.
It does not claim ownership of third-party footage.
"""

from dataclasses import asdict, dataclass
import re
from typing import Any


@dataclass
class ContentPlan:
    source: str
    source_url: str
    streamer: str
    hook: str
    narration: str
    cta: str
    title: str
    description: str
    hashtags: list[str]
    aspect_ratio: str = "9:16"
    target_duration_seconds: int = 45
    approval_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clean(text: str, fallback: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text or fallback


def build_content_plan(candidate: dict[str, Any]) -> ContentPlan:
    """Build an original commentary plan from candidate metadata.

    The narration describes the moment instead of reproducing dialogue from
    the source clip. A later AI writer can replace this template while keeping
    the same output contract.
    """
    streamer = _clean(candidate.get("streamer"), "el streamer")
    title = _clean(candidate.get("title"), "Momento inesperado en directo")
    source = _clean(candidate.get("source"), "unknown")
    url = _clean(candidate.get("url"), "")

    hook = f"No vas a creer lo que pasó con {streamer}."
    narration = (
        f"Este momento de {streamer} está llamando la atención. "
        f"El clip muestra: {title}. "
        "La reacción y el contexto son lo que hacen que este momento destaque."
    )
    cta = "¿Tú cómo habrías reaccionado? Déjalo en los comentarios."

    hashtags = [
        "#Shorts",
        "#Viral",
        f"#{re.sub(r'[^A-Za-z0-9]', '', streamer)}",
        "#Streamer",
    ]
    hashtags = list(dict.fromkeys(h for h in hashtags if len(h) > 1))

    description = (
        f"Momento destacado de {streamer}. {title}.\n\n"
        "Contenido preparado con edición y comentario original. "
        "La publicación requiere aprobación antes de salir.\n\n"
        + " ".join(hashtags)
    )

    return ContentPlan(
        source=source,
        source_url=url,
        streamer=streamer,
        hook=hook,
        narration=narration,
        cta=cta,
        title=title[:95],
        description=description,
        hashtags=hashtags,
    )
