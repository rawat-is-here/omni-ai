"""
Stable note tracker.

Converts frame-by-frame pitch estimates
into musical note events.
"""

from __future__ import annotations

import time

from config import NOTES
from core.data_models import (
    PitchResult,
    NoteEvent,
)


class NoteTracker:

    def __init__(self):

        self.current_note = None
        self.start_time = None
        self.last_seen = None

        self.confidence_sum = 0.0
        self.frames = 0

    # ---------------------------------------------------------

    def process(
        self,
        pitch: PitchResult,
        timestamp: float | None = None,
    ):

        now = timestamp if timestamp is not None else time.perf_counter()

        # -----------------------------------------------------
        # Silence
        # -----------------------------------------------------

        if not pitch.voiced:

            return self._finish_if_needed(now)

        midi = pitch.midi_note

        # -----------------------------------------------------
        # First note
        # -----------------------------------------------------

        if self.current_note is None:

            self.current_note = midi
            self.start_time = now
            self.last_seen = now

            self.confidence_sum = pitch.confidence
            self.frames = 1

            return None

        # -----------------------------------------------------
        # Same note continues
        # -----------------------------------------------------

        if midi == self.current_note:

            self.last_seen = now
            self.frames += 1
            self.confidence_sum += pitch.confidence

            return None

        # -----------------------------------------------------
        # Different note
        # Finish current note immediately.
        # -----------------------------------------------------

        event = self._finish_current(now)

        self.current_note = midi
        self.start_time = now
        self.last_seen = now

        self.confidence_sum = pitch.confidence
        self.frames = 1

        return event

    # ---------------------------------------------------------

    def _finish_if_needed(
        self,
        now,
    ):

        if self.current_note is None:
            return None

        gap = now - self.last_seen

        if gap * 1000 < NOTES.MAX_NOTE_GAP_MS:
            return None

        return self._finish_current(self.last_seen)

    # ---------------------------------------------------------

    def _finish_current(
        self,
        end_time,
    ):

        avg_conf = self.confidence_sum / max(1, self.frames)

        event = NoteEvent(

            midi_note=self.current_note,

            note_name="",

            start_time=self.start_time,

            end_time=end_time,

            confidence=avg_conf,

            velocity=avg_conf,

        )

        self.current_note = None
        self.start_time = None
        self.last_seen = None

        self.confidence_sum = 0.0
        self.frames = 0

        # Filter out notes that are too short (noise/jitter)
        if event.duration * 1000 < NOTES.MIN_NOTE_DURATION_MS:
            return None

        return event