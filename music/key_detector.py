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

        # Extract temporal anchors
        first_note_pc = notes[0].midi_note % 12
        last_note_pc = notes[-1].midi_note % 12

        # =================================================================
        # PASS 1: Calculate Pure Diatonic Membership for all 24 scales
        # =================================================================
        candidates = []
        max_membership = -1.0

        for tonic_idx in range(12):
            shifted_major = np.roll(BINARY_MAJOR, tonic_idx)
            shifted_minor = np.roll(BINARY_MINOR, tonic_idx)

            in_scale_major = np.sum(durations * shifted_major)
            in_scale_minor = np.sum(durations * shifted_minor)
            
            score_major = in_scale_major / total_duration
            score_minor = in_scale_minor / total_duration

            candidates.append({"tonic_idx": tonic_idx, "mode": "Major", "membership": score_major})
            candidates.append({"tonic_idx": tonic_idx, "mode": "Minor", "membership": score_minor})

            max_membership = max(max_membership, score_major, score_minor)

        # Filter down to only those scales that tied for the top membership score
        # Using a tiny epsilon for float comparison safety
        epsilon = 1e-5
        top_candidates = [c for c in candidates if c["membership"] >= max_membership - epsilon]

        # =================================================================
        # PASS 2: The Differentiator Function
        # =================================================================
        best_candidate = None
        best_diff_score = -float('inf')

        for c in top_candidates:
            tonic_idx = c["tonic_idx"]
            mode = c["mode"]
            
            # 1. K-S Statistical Profile Correlation
            if mode == "Major":
                ks_profile = np.roll(KS_MAJOR_PROFILE, tonic_idx)
            else:
                ks_profile = np.roll(KS_MINOR_PROFILE, tonic_idx)
                
            if hist_std > 0:
                corr = (np.corrcoef(histogram, ks_profile)[0, 1] + 1) / 2
                if np.isnan(corr): corr = 0.0
            else:
                corr = 0.0
                
            # 2. Temporal Anchor Heuristics
            # Vocalists naturally anchor the beginning and end of phrases on the Tonic or Dominant.
            anchor_bonus = 0.0
            dominant_idx = (tonic_idx + 7) % 12
            
            # First note anchor
            if first_note_pc == tonic_idx:
                anchor_bonus += 0.05
            elif first_note_pc == dominant_idx:
                anchor_bonus += 0.02
                
            # Last note resolution anchor
            if last_note_pc == tonic_idx:
                anchor_bonus += 0.03
            elif last_note_pc == dominant_idx:
                anchor_bonus += 0.01

            # The differentiator score is the combination of statistics + temporal anchors
            diff_score = corr + anchor_bonus
            
            if diff_score > best_diff_score:
                best_diff_score = diff_score
                best_candidate = c

        # The confidence is exactly the pure membership percentage (0.0 to 1.0)
        confidence = float(max(0.0, min(1.0, max_membership)))

        return KeyEstimate(
            tonic=NOTE_NAMES[best_candidate["tonic_idx"]],
            mode=best_candidate["mode"],
            confidence=confidence
        )
