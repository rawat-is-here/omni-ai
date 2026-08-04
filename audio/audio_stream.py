"""
audio_stream.py

Handles live microphone input and exposes a clean stream
of AudioFrame objects to the rest of the application.
"""

from __future__ import annotations

import queue
import time
from typing import Iterator

import numpy as np
import sounddevice as sd

from config import AUDIO
from core.data_models import AudioFrame


class AudioStream:
    """
    Live microphone stream.

    Produces AudioFrame objects continuously.
    """

    def __init__(self):

        self._queue = queue.Queue()

        self._frame_index = 0

        self._stream = None

    def _callback(self, indata, frames, time_info, status):
        """
        Internal sounddevice callback.
        """

        if status:
            print(status)

        samples = np.copy(indata[:, 0])

        frame = AudioFrame(
            samples=samples,
            sample_rate=AUDIO.SAMPLE_RATE,
            timestamp=time.perf_counter(),
            frame_index=self._frame_index,
        )

        self._frame_index += 1

        self._queue.put(frame)

    def start(self):

        self._stream = sd.InputStream(
            samplerate=AUDIO.SAMPLE_RATE,
            blocksize=AUDIO.BUFFER_SIZE,
            channels=AUDIO.CHANNELS,
            latency=AUDIO.LATENCY,
            callback=self._callback,
        )

        self._stream.start()

    def stop(self):

        if self._stream is not None:
            self._stream.stop()
            self._stream.close()

    def frames(self) -> Iterator[AudioFrame]:
        """
        Infinite generator yielding AudioFrames.
        """

        while True:
            yield self._queue.get()