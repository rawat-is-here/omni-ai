"""
voice.py

A single continuously sounding musical voice.

Each Voice owns one oscillator and smoothly
moves between notes without restarting.
"""

from __future__ import annotations

import numpy as np

from synth.glide import Glide
from synth.rt_oscillator import RTOscillator


class Voice:
    """
    One continuously running oscillator.

    It never restarts when a chord changes.
    Only its target frequency changes.
    """

    def __init__(

        self,

        sample_rate: int = 44100,

    ):

        self.sample_rate = sample_rate

        self.oscillator = RTOscillator(sample_rate)

        self.frequency = 440.0

        self.glide = Glide(

            initial=self.frequency,

            sample_rate=sample_rate,

        )

        self.gain = 0.0

        self.target_gain = 0.0

        self.attack = 0.002

        self.release = 0.003

        self.active = False

        self.current_note = None

    # ---------------------------------------------------------

    @staticmethod
    def midi_to_frequency(

        midi_note: int,

    ) -> float:

        return 440.0 * (

            2.0 ** (

                (midi_note - 69) / 12.0

            )

        )

    # ---------------------------------------------------------

    def set_note(

        self,

        midi_note: int,

        velocity: float = 1.0,

    ):

        self.current_note = midi_note

        target = self.midi_to_frequency(

            midi_note

        )

        self.glide.set_target(target)

        self.target_gain = max(

            0.0,

            min(

                velocity,

                1.0,

            ),

        )

        self.active = True

    # ---------------------------------------------------------

    def release_note(self):

        self.target_gain = 0.0

    # ---------------------------------------------------------

    def render(

        self,

        frames: int,

    ) -> np.ndarray:

        frequencies = np.empty(

            frames,

            dtype=np.float32,

        )

        for i in range(frames):

            frequencies[i] = self.glide.next_value()

        wave = self.oscillator.render(

            frequencies

        )

        output = np.empty(

            frames,

            dtype=np.float32,

        )

        gain = self.gain

        for i in range(frames):

            if gain < self.target_gain:

                gain = min(

                    self.target_gain,

                    gain + self.attack,

                )

            elif gain > self.target_gain:

                gain = max(

                    self.target_gain,

                    gain - self.release,

                )

            output[i] = wave[i] * gain

        self.gain = gain

        if (

            gain <= 0.0001

            and

            self.target_gain == 0.0

        ):

            self.active = False

            self.current_note = None

        return output