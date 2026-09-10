#!/usr/bin/env python3
"""Create a local French Kokoro audio file.

Examples:
  .kokoro-env/bin/python kokoro_french.py "Bonjour, comment allez-vous ?"
  .kokoro-env/bin/python kokoro_french.py --output audio/lesson-01.wav "..."
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from kokoro_mlx import KokoroTTS


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate French speech locally with Kokoro.")
    parser.add_argument("text", nargs="*", help="French text to turn into audio.")
    parser.add_argument("--output", default="audio/kokoro-french.wav", help="WAV file to create.")
    parser.add_argument("--speed", type=float, default=1.0, help="Speaking speed (default: 1.0).")
    args = parser.parse_args()

    text = " ".join(args.text).strip() or sys.stdin.read().strip()
    if not text:
        parser.error("provide French text as an argument or through standard input")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    # ff_siwis is Kokoro's built-in French female voice.
    with KokoroTTS.from_pretrained() as tts:
        result = tts.save(text, str(output), voice="ff_siwis", speed=args.speed, language="fr")

    print(f"Created {output} ({result.duration:.1f} seconds).")


if __name__ == "__main__":
    main()
