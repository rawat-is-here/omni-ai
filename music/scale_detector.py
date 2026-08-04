"""
music/scale_detector.py

Real-time probabilistic scale detector.

This module estimates the musical mode
(Ionian, Dorian, Aeolian, etc.)
from the recent NoteEvents stored
inside MusicMemory.

It DOES NOT determine the tonic/key.
"""

from __future__ import annotations

from collections import defaultdict

from core.data_models import ScaleResult
from music.music_memory import MusicMemory
from music.theory import MODES


class ScaleDetector:

    """
    Detects the most likely musical scale
    using weighted pitch-class statistics.
    """

    def __init__(self):

        self.minimum_notes = 4

    # -----------------------------------------------------

    def detect(
        self,
        memory: MusicMemory,
    ) -> ScaleResult | None:

        notes = memory.get_notes()

        if len(notes) < self.minimum_notes:
            return None

        pitch_weights = defaultdict(float)

        total_weight = 0.0

        # ----------------------------------------------
        # Build weighted pitch-class histogram
        # ----------------------------------------------

        for note in notes:

            pitch_class = note.midi_note % 12

            duration = max(0.05, note.duration)

            confidence = max(0.0, note.confidence)

            weight = duration * confidence

            pitch_weights[pitch_class] += weight

            total_weight += weight

        if total_weight == 0:
            return None

        # ----------------------------------------------
        # Score every musical mode
        # ----------------------------------------------

        best_mode = None

        best_score = float("-inf")

        for mode_name, intervals in MODES.items():

            score = 0.0

            for pc, weight in pitch_weights.items():

                if pc in intervals:

                    score += weight

                else:

                    score -= weight * 2.0

            if score > best_score:

                best_score = score

                best_mode = mode_name

        confidence = max(
            0.0,
            min(
                1.0,
                best_score / total_weight
            )
        )

        return ScaleResult(

            mode=best_mode,

            confidence=confidence,

            pitch_classes=tuple(sorted(pitch_weights.keys()))
        )