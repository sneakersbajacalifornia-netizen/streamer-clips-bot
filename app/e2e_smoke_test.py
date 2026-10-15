from pathlib import Path
import subprocess

from app.tts import synthesize
from app.render import render_short

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "data" / "test"
SOURCE = TEST / "source.mp4"
VOICE = TEST / "narration.wav"
OUTPUT = TEST / "short.mp4"


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    TEST.mkdir(parents=True, exist_ok=True)

    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100",
        "-t", "10",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", str(SOURCE),
    ])

    synthesize(
        "Esta es una prueba del sistema automático de Shorts.",
        VOICE,
    )
    render_short(SOURCE, OUTPUT, voice_audio=VOICE)

    probe = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0", str(OUTPUT),
    ], text=True).strip()

    if probe != "1080x1920":
        raise RuntimeError(f"Unexpected video size: {probe}")

    print(f"E2E OK: {OUTPUT} ({probe})")


if __name__ == "__main__":
    main()
