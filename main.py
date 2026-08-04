"""
OmniAI

Main application entry point.

Listens to the microphone,
detects notes,
predicts accompaniment,
and plays it live.
"""

from __future__ import annotations

import traceback

from runtime.audio_pipeline import AudioPipeline
from runtime.controller import RuntimeController


def main():

    print("=" * 60)
    print("OmniAI")
    print("=" * 60)
    print()
    print("Listening...")
    print("Press Ctrl+C to quit.")
    print()

    pipeline = AudioPipeline()
    pipeline.start()
    controller = RuntimeController()

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

        controller.clear()

        print("Goodbye.")


if __name__ == "__main__":

    main()