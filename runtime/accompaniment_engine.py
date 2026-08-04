"""
OmniAI Runtime Engine

Coordinates the AI, harmony engine,
and synthesizer.
"""

from __future__ import annotations

import numpy as np

from ai.inference import OmniInference

from harmony.chord_selector import ChordSelector

from synth.synth_engine import SynthEngine


class AccompanimentEngine:

    def __init__(self):

        self.ai = OmniInference()

        self.selector = ChordSelector()

        self.synth = SynthEngine()

    # --------------------------------------------------------

    def predict(
        self,
        melody: list[int],
    ):

        return self.ai.predict(melody)

    # --------------------------------------------------------

    def render(
        self,
        prediction: dict,
        duration: float = 1.0,
    ) -> np.ndarray:

        harmony = self.selector.build(

            prediction["root"],

            prediction["quality"],

        )

        audio = self.synth.render(

            harmony,

            duration,

        )

        return audio

    # --------------------------------------------------------

    def process(
        self,
        melody: list[int],
        duration: float = 1.0,
    ) -> np.ndarray:

        prediction = self.predict(melody)

        return self.render(

            prediction,

            duration,

        )