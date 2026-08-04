"""
High-quality autocorrelation pitch detector.

This is our baseline pitch detector.
Future detectors (YIN, CREPE, RMVPE) will implement
the same interface.
"""

from __future__ import annotations

import numpy as np

from config import PITCH
from core.data_models import (
    AudioFrame,
    PitchResult,
    VoiceActivityResult,
)

from .base import PitchDetector

NOTE_NAMES = [
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
]


class AutoCorrelationPitchDetector(PitchDetector):

    def process(
        self,
        frame: AudioFrame,
        voice: VoiceActivityResult,
    ) -> PitchResult:

        if not voice.is_voiced:
            return PitchResult(
                frequency=0.0,
                midi_note=None,
                note_name=None,
                octave=None,
                confidence=0.0,
                voiced=False,
            )

        samples = frame.samples.astype(np.float64)

        samples -= np.mean(samples)

        window = np.hanning(len(samples))

        samples *= window

        corr = np.correlate(samples, samples, mode="full")

        corr = corr[len(corr)//2:]

        if corr[0] <= 0:
            return self._empty()

        corr /= corr[0]

        min_lag = int(frame.sample_rate / PITCH.MAX_FREQUENCY)

        max_lag = int(frame.sample_rate / PITCH.MIN_FREQUENCY)

        search = corr[min_lag:max_lag]

        peak = np.argmax(search)

        lag = peak + min_lag

        confidence = float(search[peak])

        if confidence < PITCH.MIN_CORRELATION:
            return self._empty()

        frequency = frame.sample_rate / lag

        midi = int(round(
            69 + 12 * np.log2(frequency / 440.0)
        ))

        note_index = midi % 12

        octave = (midi // 12) - 1

        note_name = NOTE_NAMES[note_index]

        return PitchResult(
            frequency=float(frequency),
            midi_note=midi,
            note_name=note_name,
            octave=octave,
            confidence=confidence,
            voiced=True,
        )

    def _empty(self):

        return PitchResult(
            frequency=0.0,
            midi_note=None,
            note_name=None,
            octave=None,
            confidence=0.0,
            voiced=False,
        )