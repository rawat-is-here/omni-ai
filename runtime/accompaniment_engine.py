"""
Accompaniment Engine

Coordinates the AI prediction,
voice leading and realtime synthesis.
"""

from __future__ import annotations

from ai.inference import OmniInference

from harmony.chord_selector import ChordSelector
from harmony.voice_leading import VoiceLeading

from synth.realtime_synth import RealtimeSynth


class AccompanimentEngine:

    def __init__(self):

        self.ai = OmniInference()

        self.selector = ChordSelector()

        self.voice_leading = VoiceLeading()

        self.synth = RealtimeSynth()

        self.last_prediction = None

    # --------------------------------------------------------

    def process(
        self,
        melody: list[int],
    ) -> dict:

        prediction = self.ai.predict(
            melody,
        )

        self.last_prediction = prediction

        harmony = self.selector.build(

            prediction["root"],

            prediction["quality"],

        )

        notes = self.voice_leading.apply(
            harmony,
        )

        self.synth.set_chord(
            notes,
            velocity=0.90,
        )

        return prediction

    # --------------------------------------------------------

    def current_prediction(self):

        return self.last_prediction

    # --------------------------------------------------------

    def silence(self):

        self.synth.silence()

    # --------------------------------------------------------

    def stop(self):

        self.synth.stop()


# ------------------------------------------------------------

if __name__ == "__main__":

    import time

    engine = AccompanimentEngine()

    melody = [

        60,
        62,
        64,
        65,
        67,
        69,
        71,
        72,

    ]

    result = engine.process(melody)

    print(result)

    print("Playing...")

    time.sleep(5)

    engine.stop()