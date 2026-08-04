"""
music_memory.py

Maintains a rolling musical context for the AI.

This module stores recent NoteEvents and computes
high-level musical statistics that later modules
(Key Detector, AI, Harmony Engine) can use.
"""

from __future__ import annotations

from collections import deque
from statistics import mean

from core.data_models import NoteEvent


class MusicMemory:
    """
    Rolling memory of recent musical events.
    """

    def __init__(self, max_notes: int = 32):

        self.notes = deque(maxlen=max_notes)

    # --------------------------------------------------

    def add(self, note: NoteEvent):

        """
        Add a finished note event.
        """

        self.notes.append(note)

    # --------------------------------------------------

    def clear(self):

        self.notes.clear()

    # --------------------------------------------------

    def get_notes(self):

        return list(self.notes)

    # --------------------------------------------------

    def is_empty(self):

        return len(self.notes) == 0
    def average_pitch(self):

        if not self.notes:
            return None

        return mean(
            note.midi_note
            for note in self.notes
        )

    # --------------------------------------------------

    def average_duration(self):

        if not self.notes:
            return 0.0

        return mean(
            note.duration
            for note in self.notes
        )
    def melodic_direction(self):

        """
        Returns

        "ascending"

        "descending"

        "static"

        "mixed"
        """

        if len(self.notes) < 2:
            return "unknown"

        diffs = []

        notes = list(self.notes)

        for a, b in zip(notes[:-1], notes[1:]):

            diffs.append(
                b.midi_note - a.midi_note
            )

        if all(d > 0 for d in diffs):
            return "ascending"

        if all(d < 0 for d in diffs):
            return "descending"

        if all(d == 0 for d in diffs):
            return "static"

        return "mixed"
    def phrase_duration(self):

        if len(self.notes) < 2:
            return 0.0

        return (
            self.notes[-1].end_time
            -
            self.notes[0].start_time
        )
    def notes_per_second(self):

        duration = self.phrase_duration()

        if duration <= 0:
            return 0.0

        return len(self.notes) / duration