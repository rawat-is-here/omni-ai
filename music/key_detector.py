"""
music/key_detector.py

Real-time key detector using the Krumhansl-Schmuckler (K-S) key-finding algorithm.
Determines both the tonic (e.g. C, A) and mode (Major, Minor) of singing.
"""

from __future__ import annotations

import numpy as np

from core.data_models import KeyEstimate
from music.music_memory import MusicMemory
from music.theory import NOTE_NAMES

# Krumhansl-Schmuckler Key Profiles (relative to C)
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


class KeyDetector:
    def __init__(self):
        self.minimum_notes = 4

    def detect(self, memory: MusicMemory) -> KeyEstimate | None:
        notes = memory.get_notes()
        if len(notes) < self.minimum_notes:
            return None

        # Build weighted pitch-class histogram with recency decay
        histogram = np.zeros(12, dtype=np.float32)
        total_weight = 0.0
        decay_factor = 0.9  # Decay weight of older notes by 10% per step

        for i, note in enumerate(reversed(notes)):
            pc = note.midi_note % 12
            duration = max(0.05, note.duration)
            confidence = max(0.0, note.confidence)
            # Recent notes are exponentially weighted higher
            weight = duration * confidence * (decay_factor ** i)
            histogram[pc] += weight
            total_weight += weight

        if total_weight == 0.0:
            return None

        # Normalize histogram
        histogram /= total_weight

        best_key = None
        best_mode = None
        best_r = -2.0  # Pearson correlation range is [-1, 1]

        # Check all 12 tonics for Major and Minor
        for tonic_idx in range(12):
            # Shift profiles to tonic_idx
            shifted_major = np.roll(MAJOR_PROFILE, tonic_idx)
            shifted_minor = np.roll(MINOR_PROFILE, tonic_idx)

            # Pearson correlation
            r_major = np.corrcoef(histogram, shifted_major)[0, 1]
            r_minor = np.corrcoef(histogram, shifted_minor)[0, 1]

            if r_major > best_r:
                best_r = r_major
                best_key = NOTE_NAMES[tonic_idx]
                best_mode = "Major"

            if r_minor > best_r:
                best_r = r_minor
                best_key = NOTE_NAMES[tonic_idx]
                best_mode = "Minor"

        # Map correlation to 0-1 confidence range
        confidence = float(max(0.0, min(1.0, (best_r + 1.0) / 2.0)))

        return KeyEstimate(
            tonic=best_key,
            mode=best_mode,
            confidence=confidence
        )
