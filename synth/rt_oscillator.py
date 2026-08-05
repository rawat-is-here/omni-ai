"""
rt_oscillator.py

Low-level continuous oscillator.

Unlike the previous implementation,
this oscillator knows nothing about
MIDI notes or chords.

It simply generates one waveform from
a continuously changing frequency.
"""

from __future__ import annotations

import math

import numpy as np


class RTOscillator:
    """
    Continuous oscillator.

    Phase is never reset.
    Frequency may change every sample.
    """

    def __init__(

        self,

        sample_rate: int = 44100,

    ):

        self.sample_rate = sample_rate

        self.phase = 0.0

    # ------------------------------------------------------------

    def reset(self):

        self.phase = 0.0

    # ------------------------------------------------------------

    def render(

        self,

        frequencies: np.ndarray,

    ) -> np.ndarray:

        """
        Render one block.

        frequencies

            One frequency value per sample.

        Returns

            float32 waveform.
        """

        frames = len(frequencies)

        output = np.empty(

            frames,

            dtype=np.float32,

        )

        phase = self.phase

        sr = self.sample_rate

        two_pi = 2.0 * math.pi

        for i in range(frames):

            phase += (

                two_pi

                * frequencies[i]

                / sr

            )

            if phase >= two_pi:

                phase -= two_pi

            x = phase / two_pi

            sine = math.sin(phase)

            triangle = (

                2.0

                * abs(

                    2.0 * (x % 1.0)

                    - 1.0

                )

                - 1.0

            )

            saw = (

                2.0

                * (x % 1.0)

                - 1.0

            )

            output[i] = (

                0.55 * sine

                +

                0.30 * triangle

                +

                0.15 * saw

            )

        self.phase = phase

        return output