"""
speaker.py

Continuous audio output for OmniAI.
"""

from __future__ import annotations

import queue

import numpy as np
import sounddevice as sd


class Speaker:

    def __init__(self, sample_rate: int = 44100):

        self.sample_rate = sample_rate

        self.queue = queue.Queue()

        self.current = np.zeros(0, dtype=np.float32)
        self.position = 0

        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=self._callback,
        )

        self.stream.start()

    # ---------------------------------------------------------

    def _callback(self, outdata, frames, time, status):

        if status:
            print(status)

        out = np.zeros(frames, dtype=np.float32)

        written = 0

        while written < frames:

            # Need a new audio buffer?
            if self.position >= len(self.current):

                try:
                    self.current = self.queue.get_nowait()
                    self.position = 0
                except queue.Empty:
                    break

            remaining = len(self.current) - self.position

            n = min(remaining, frames - written)

            out[written:written + n] = self.current[
                self.position:self.position + n
            ]

            written += n
            self.position += n

        outdata[:, 0] = out

    # ---------------------------------------------------------

    def play(self, audio: np.ndarray):

        if audio is None:
            return

        if len(audio) == 0:
            return

        audio = np.asarray(audio, dtype=np.float32)

        peak = np.max(np.abs(audio))

        if peak > 1.0:
            audio /= peak

        self.queue.put(audio)

    # ---------------------------------------------------------

    def stop(self):

        self.stream.stop()
        self.stream.close()