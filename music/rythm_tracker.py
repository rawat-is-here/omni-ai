"""
Rhythm Tracker

Analyzes note timing and articulation.

This module is independent of tempo.
"""

from __future__ import annotations

from statistics import mean, pstdev

from core.data_models import RhythmInfo
from music.music_memory import MusicMemory

class RhythmTracker:

    def __init__(self):

        self.minimum_notes = 4

    def analyze(
        self,
        memory: MusicMemory,
    ) -> RhythmInfo | None:

        notes = memory.get_notes()

        if len(notes) < self.minimum_notes:
            return None
        durations = [
            note.duration
            for note in notes
        ]

        avg_duration = mean(durations)
        gaps = []

        for previous, current in zip(
            notes[:-1],
            notes[1:]
        ):

            gaps.append(
                max(
                    0.0,
                    current.start_time - previous.end_time
                )
            )

        avg_gap = mean(gaps) if gaps else 0.0
        phrase_time = (
            notes[-1].end_time
            -
            notes[0].start_time
        )

        density = (
            len(notes)
            /
            max(0.001, phrase_time)
        )
        ratio = avg_gap / max(avg_duration, 0.001)

        if ratio < 0.15:

            articulation = "legato"

        elif ratio < 0.45:

            articulation = "normal"

        else:

            articulation = "staccato"
        if len(durations) > 1:

            variation = pstdev(durations)

            stability = max(
                0.0,
                1.0 - variation
            )

        else:

            stability = 1.0
        return RhythmInfo(

            average_note_duration=avg_duration,

            average_gap=avg_gap,

            notes_per_second=density,

            articulation=articulation,

            rhythmic_stability=stability,
        )