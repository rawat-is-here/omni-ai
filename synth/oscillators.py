"""
Basic Oscillator Bank for OmniAI.
"""

from __future__ import annotations

import numpy as np


SAMPLE_RATE = 44100


class OscillatorBank:

    def __init__(self):

        self.sample_rate = SAMPLE_RATE

    # ---------------------------------------------------------

    @staticmethod
    def midi_to_frequency(midi: int) -> float:

        return 440.0 * (2 ** ((midi - 69) / 12))

    # ---------------------------------------------------------

    def sine(
        self,
        frequency: float,
        duration: float,
    ):

        t = np.linspace(
            0,
            duration,
            int(self.sample_rate * duration),
            endpoint=False,
        )

        return np.sin(
            2 * np.pi * frequency * t
        )

    # ---------------------------------------------------------

    def triangle(
        self,
        frequency: float,
        duration: float,
    ):

        t = np.linspace(
            0,
            duration,
            int(self.sample_rate * duration),
            endpoint=False,
        )

        return (
            2
            * np.abs(
                2 * ((frequency * t) % 1) - 1
            )
            - 1
        )

    # ---------------------------------------------------------

    def saw(
        self,
        frequency,
        duration,
    ):

        t = np.linspace(
            0,
            duration,
            int(self.sample_rate * duration),
            endpoint=False,
        )

        return 2 * ((frequency * t) % 1) - 1

    # ---------------------------------------------------------

    def square(
        self,
        frequency,
        duration,
    ):

        t = np.linspace(
            0,
            duration,
            int(self.sample_rate * duration),
            endpoint=False,
        )

        return np.sign(

            np.sin(
                2 * np.pi * frequency * t
            )

        )

    # ---------------------------------------------------------

    def chord(
        self,
        midi_notes: list[int],
        duration: float = 1.0,
    ):
        output = np.zeros(
            int(duration * self.sample_rate),
            dtype=np.float32,
        )
        if not midi_notes:
            return output

        for note in midi_notes:
            f = self.midi_to_frequency(note)
            
            # Detuned frequencies
            f_center = f
            f_left = f * 2.0**(-7.0 / 1200.0)
            f_right = f * 2.0**(+7.0 / 1200.0)
            f_sub = f * 0.5
            
            # Generate and mix waves
            # Center: 40% sine/triangle mix
            wave_center = 0.4 * self.sine(f_center, duration) + 0.6 * self.triangle(f_center, duration)
            # Left: 20% saw/triangle mix
            wave_left = 0.3 * self.saw(f_left, duration) + 0.7 * self.triangle(f_left, duration)
            # Right: 20% saw/triangle mix
            wave_right = 0.3 * self.saw(f_right, duration) + 0.7 * self.triangle(f_right, duration)
            # Sub: 20% pure sine
            wave_sub = self.sine(f_sub, duration)
            
            wave = 0.40 * wave_center + 0.20 * wave_left + 0.20 * wave_right + 0.20 * wave_sub
            output += wave

        output /= len(midi_notes)
        peak = np.max(np.abs(output))
        if peak > 0:
            output /= peak

        return output.astype(np.float32)


# ---------------------------------------------------------

if __name__ == "__main__":

    osc = OscillatorBank()

    chord = osc.chord(

        [60, 64, 67],

        duration=2,

    )

    print(chord.shape)

    print(chord.min(), chord.max())