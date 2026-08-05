"""
OmniAI

Main application entry point.

Listens to the microphone,
detects notes,
predicts accompaniment,
and plays it live.
"""

from __future__ import annotations

import argparse
import traceback

from runtime.audio_pipeline import AudioPipeline
from runtime.controller import RuntimeController


def main():

    parser = argparse.ArgumentParser(description="OmniAI Live Accompanist")
    parser.add_argument("--key", type=str, help="Lock to a specific key, e.g., 'C Major' or 'A Minor'")
    args = parser.parse_args()

    print("=" * 60)
    print("OmniAI")
    print("=" * 60)
    print()
    print("Listening...")
    print("Press Ctrl+C to quit.")
    print()

    pipeline = AudioPipeline()
    pipeline.start()
    controller = RuntimeController(fixed_key_str=args.key)

    try:

        for note in pipeline.notes():

            if note is None:
                continue

            controller.add_note(note)

            controller.update()

    except KeyboardInterrupt:

        print()
        print("Stopping OmniAI...")

    except Exception:

        print()
        print("Unexpected error:")
        traceback.print_exc()

    finally:
        pipeline.stop()
        
        # controller.stop()

        controller.clear()

        print("Goodbye.")


if __name__ == "__main__":

    main()