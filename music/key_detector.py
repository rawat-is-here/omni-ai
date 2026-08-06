"""
music/key_detector.py

Real-time key detector using the Krumhansl-Schmuckler (K-S) key-finding algorithm.
Determines both the tonic (e.g. C, A) and mode (Major, Minor) of singing.
"""

from __future__ import annotations

import numpy as np

from core.data_models import KeyEstimate
from music.theory import NOTE_NAMES

# Binary scale templates (1 if note belongs to scale, 0 if not)
# Major intervals: 0, 2, 4, 5, 7, 9, 11
BINARY_MAJOR = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1], dtype=np.float32)

# Natural Minor intervals: 0, 2, 3, 5, 7, 8, 10
BINARY_MINOR = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0], dtype=np.float32)

# Krumhansl-Schmuckler Key Profiles (empirical dataset for major/minor distinction)
KS_MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KS_MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


class KeyDetector:
    def __init__(self):
        pass

    def detect(self, memory: 'MusicMemory') -> KeyEstimate | None:
        notes = memory.get_notes()
        if len(notes) == 0:
            return None

        # Accumulate pitch-class durations
        durations = np.zeros(12, dtype=np.float32)
        total_duration = 0.0

        for note in notes:
            pc = note.midi_note % 12
            weight = note.duration * note.confidence
            durations[pc] += weight
            total_duration += weight

        if total_duration == 0.0:
            return None

        histogram = durations / total_duration
        hist_std = np.std(histogram)

        best_key = None
        best_mode = None
        best_score = -1.0
        best_membership = 0.0

        # Test all 12 tonics for Major and Minor
        for tonic_idx in range(12):
            shifted_major = np.roll(BINARY_MAJOR, tonic_idx)
            shifted_minor = np.roll(BINARY_MINOR, tonic_idx)

            # Calculate membership percentage: What % of sung duration is in the scale?
            in_scale_major = np.sum(durations * shifted_major)
            in_scale_minor = np.sum(durations * shifted_minor)
            
            score_major = in_scale_major / total_duration
            score_minor = in_scale_minor / total_duration

            # Tie-breaker: Use K-S empirical dataset to distinguish relative major/minor
            ks_shifted_major = np.roll(KS_MAJOR_PROFILE, tonic_idx)
            ks_shifted_minor = np.roll(KS_MINOR_PROFILE, tonic_idx)
            
            if hist_std > 0:
                corr_major = (np.corrcoef(histogram, ks_shifted_major)[0, 1] + 1) / 2
                corr_minor = (np.corrcoef(histogram, ks_shifted_minor)[0, 1] + 1) / 2
                # Handle possible NaN if variance is extremely low despite std > 0 check
                if np.isnan(corr_major): corr_major = 0.0
                if np.isnan(corr_minor): corr_minor = 0.0
            else:
                corr_major = 0.0
                corr_minor = 0.0
            
            # Weight the membership heavily (99%), and use K-S statistical dataset (1%) to break ties
            final_major = (score_major * 0.99) + (corr_major * 0.01)
            final_minor = (score_minor * 0.99) + (corr_minor * 0.01)

            if final_major > best_score:
                best_score = final_major
                best_key = NOTE_NAMES[tonic_idx]
                best_mode = "Major"
                best_membership = score_major

            if final_minor > best_score:
                best_score = final_minor
                best_key = NOTE_NAMES[tonic_idx]
                best_mode = "Minor"
                best_membership = score_minor

        # The confidence is exactly the pure membership percentage (0.0 to 1.0)
        confidence = float(max(0.0, min(1.0, best_membership)))

        return KeyEstimate(
            tonic=best_key,
            mode=best_mode,
            confidence=confidence
        )
