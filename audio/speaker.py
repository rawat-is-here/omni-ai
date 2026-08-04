"""
speaker.py

Simple audio output for OmniAI.

Plays synthesized accompaniment through the speakers.
"""

from __future__ import annotations

import numpy as np
import sounddevice as sd


class Speaker:

    def __init__(self, sample_rate: int = 44100):

        self.sample_rate = sample_rate

    # -----------------------------------------------------

    def play(self, audio: np.ndarray):

        """
        Play a numpy waveform.
        """

        if audio is None:
            return

        if len(audio) == 0:
            return

        audio = np.asarray(audio, dtype=np.float32)

        peak = np.max(np.abs(audio))

        if peak > 1.0:
            audio = audio / peak

        sd.play(audio, self.sample_rate)

    # -----------------------------------------------------

    def play_blocking(self, audio: np.ndarray):

        """
        Play and wait until finished.
        Useful for testing.
        """

        self.play(audio)

        sd.wait()

    # -----------------------------------------------------

    def stop(self):

        sd.stop()