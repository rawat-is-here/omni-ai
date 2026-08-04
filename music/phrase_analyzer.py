"""
phrase_analyzer.py

Analyzes the recent musical phrase.

This module converts a stream of NoteEvents
into higher-level phrase information that
can be used by the harmony engine and AI.
"""

from __future__ import annotations

from statistics import mean

from core.data_models import PhraseInfo
from music.music_memory import MusicMemory

class PhraseAnalyzer:

    def __init__(self):

        self.minimum_notes = 4

    def analyze(
        self,
        memory: MusicMemory,
    ) -> PhraseInfo | None:

        notes = memory.get_notes()

        if len(notes) < self.minimum_notes:
            return None
        
        phrase_duration = (
            notes[-1].end_time
            -
            notes[0].start_time
        )
        avg_duration = mean(
            note.duration
            for note in notes
        )
        gaps = []

        for previous, current in zip(
            notes[:-1],
            notes[1:]
        ):

            gap = current.start_time - previous.end_time

            gaps.append(max(0.0, gap))

        average_gap = (
            mean(gaps)
            if gaps
            else 0.0
        )
        differences = []

        for previous, current in zip(
            notes[:-1],
            notes[1:]
        ):

            differences.append(
                current.midi_note
                -
                previous.midi_note
            )

        if all(x > 0 for x in differences):
            contour = "ascending"

        elif all(x < 0 for x in differences):
            contour = "descending"

        elif all(x == 0 for x in differences):
            contour = "static"

        else:
            contour = "mixed"
        density = (
            len(notes)
            /
            max(0.001, phrase_duration)
        )
        phrase_complete = average_gap > 0.25
        
        confidence = mean(
            note.confidence
            for note in notes
        )
        return PhraseInfo(

            note_count=len(notes),

            duration=phrase_duration,

            average_note_duration=avg_duration,

            average_gap=average_gap,

            contour=contour,

            density=density,

            phrase_complete=phrase_complete,

            confidence=confidence,
        )