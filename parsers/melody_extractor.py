"""
melody_extractor.py

Extracts the melody line from a collection of NoteEvents.

Version 1:
----------
Uses a simple but effective heuristic:
    • Notes starting at nearly the same time are grouped.
    • The highest note of each group is assumed to be the melody.

Later versions will use AI.
"""

from __future__ import annotations

from typing import List

from core.data_models import NoteEvent


class MelodyExtractor:
    """
    Extracts the melody from polyphonic music.
    """

    def __init__(self, grouping_threshold: float = 0.05):
        """
        Parameters
        ----------
        grouping_threshold:
            Notes beginning within this many seconds are
            considered part of the same chord.
        """
        self.grouping_threshold = grouping_threshold

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def extract(self, notes: List[NoteEvent]) -> List[NoteEvent]:

        if not notes:
            return []

        notes = sorted(notes, key=lambda n: n.start_time)

        groups = self._group_notes(notes)

        melody = []

        for group in groups:

            highest = max(
                group,
                key=lambda n: n.midi_note
            )

            melody.append(highest)

        melody = self._remove_duplicates(melody)

        return melody

    # ---------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------

    def _group_notes(
        self,
        notes: List[NoteEvent]
    ) -> List[List[NoteEvent]]:

        groups = []

        current_group = [notes[0]]

        reference_time = notes[0].start_time

        for note in notes[1:]:

            if (
                note.start_time - reference_time
                <= self.grouping_threshold
            ):
                current_group.append(note)

            else:

                groups.append(current_group)

                current_group = [note]

                reference_time = note.start_time

        groups.append(current_group)

        return groups

    def _remove_duplicates(
        self,
        melody: List[NoteEvent]
    ) -> List[NoteEvent]:

        if not melody:
            return []

        cleaned = [melody[0]]

        for note in melody[1:]:

            previous = cleaned[-1]

            if note.midi_note != previous.midi_note:
                cleaned.append(note)

        return cleaned


# ---------------------------------------------------------
# Debug
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("MelodyExtractor")
    print("=" * 60)
    print("This module is intended to be used by DatasetBuilder.")