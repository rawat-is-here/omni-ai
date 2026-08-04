"""
rt_oscillator.py

Continuous real-time oscillator for OmniAI.

Unlike OscillatorBank, this oscillator never
restarts phase, making it suitable for a
continuous OutputStream.
"""

from __future__ import annotations

import math

import numpy as np


class RTOscillator:

    SAMPLE_RATE = 44100

    def __init__(self):

        self.sample_rate = self.SAMPLE_RATE

        # one phase per MIDI note
        self.phase = {}

    # -----------------------------------------------------

    @staticmethod
    def midi_to_frequency(midi: int):

        return 440.0 * (2 ** ((midi - 69) / 12))

    # -----------------------------------------------------

    def render_note(
        self,
        midi: int,
        frames: int,
    ) -> np.ndarray:

        frequency = self.midi_to_frequency(midi)

        phase = self.phase.get(midi, 0.0)

        increment = (
            2.0
            * math.pi
            * frequency
            / self.sample_rate
        )

        output = np.empty(
            frames,
            dtype=np.float32,
        )

        for i in range(frames):

            output[i] = (

                0.55 * math.sin(phase)

                +

                0.30
                * (
                    2
                    * abs(
                        2
                        * (
                            phase
                            / (2 * math.pi)
                            % 1
                        )
                        - 1
                    )
                    - 1
                )

                +

                0.15
                * (
                    2
                    * (
                        phase
                        / (2 * math.pi)
                        % 1
                    )
                    - 1
                )

            )

            phase += increment

            if phase >= 2 * math.pi:

                phase -= 2 * math.pi

        self.phase[midi] = phase

        return output

    # -----------------------------------------------------

    def render_chord(
        self,
        midi_notes: list[int],
        frames: int,
    ) -> np.ndarray:

        output = np.zeros(
            frames,
            dtype=np.float32,
        )

        if not midi_notes:

            return output

        for note in midi_notes:

            output += self.render_note(
                note,
                frames,
            )

        output /= len(midi_notes)

        peak = np.max(np.abs(output))

        if peak > 1:

            output /= peak

        return output