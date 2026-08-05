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

        self.phase_center = 0.0

        self.phase_left = 0.0

        self.phase_right = 0.0

        self.phase_sub = 0.0

    # ------------------------------------------------------------

    def reset(self):

        self.phase_center = 0.0

        self.phase_left = 0.0

        self.phase_right = 0.0

        self.phase_sub = 0.0

    # ------------------------------------------------------------

    def render(

        self,

        frequencies: np.ndarray,

    ) -> np.ndarray:

        """

        Render one block with multi-oscillator detuning.

        """

        frames = len(frequencies)

        sr = self.sample_rate

        two_pi = 2.0 * np.pi



        # 1. Center Oscillator (f)

        d_phase_center = (two_pi * frequencies) / sr

        phases_center = self.phase_center + np.cumsum(d_phase_center)

        self.phase_center = phases_center[-1] % two_pi

        phases_center = phases_center % two_pi



        # 2. Left Detuned (-7 cents: f * 2^(-7/1200))

        d_phase_left = (two_pi * frequencies * 0.995968) / sr

        phases_left = self.phase_left + np.cumsum(d_phase_left)

        self.phase_left = phases_left[-1] % two_pi

        phases_left = phases_left % two_pi



        # 3. Right Detuned (+7 cents: f * 2^(+7/1200))

        d_phase_right = (two_pi * frequencies * 1.004051) / sr

        phases_right = self.phase_right + np.cumsum(d_phase_right)

        self.phase_right = phases_right[-1] % two_pi

        phases_right = phases_right % two_pi



        # 4. Sub Oscillator (-1 octave: f * 0.5)

        d_phase_sub = (two_pi * frequencies * 0.5) / sr

        phases_sub = self.phase_sub + np.cumsum(d_phase_sub)

        self.phase_sub = phases_sub[-1] % two_pi

        phases_sub = phases_sub % two_pi



        # Wave generation helper

        def generate_waves(phases):

            x = phases / two_pi

            sine = np.sin(phases)

            triangle = 2.0 * np.abs(2.0 * (x % 1.0) - 1.0) - 1.0

            saw = 2.0 * (x % 1.0) - 1.0

            return sine, triangle, saw



        # Center: warm blend of sine (40%) and triangle (60%)

        c_sine, c_tri, _ = generate_waves(phases_center)

        wave_center = 0.40 * c_sine + 0.60 * c_tri



        # Left/Right detuned: blend of triangle (70%) and saw (30%)

        _, l_tri, l_saw = generate_waves(phases_left)

        wave_left = 0.70 * l_tri + 0.30 * l_saw



        _, r_tri, r_saw = generate_waves(phases_right)

        wave_right = 0.70 * r_tri + 0.30 * r_saw



        # Sub: pure sine wave

        sub_sine, _, _ = generate_waves(phases_sub)

        wave_sub = sub_sine



        # Mix everything together

        output = (

            0.40 * wave_center

            + 0.20 * wave_left

            + 0.20 * wave_right

            + 0.20 * wave_sub

        )



        return output.astype(np.float32)