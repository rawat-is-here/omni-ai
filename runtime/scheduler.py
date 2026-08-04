"""
scheduler.py

Musical scheduler for OmniAI.

Decides when the AI should generate a new
accompaniment instead of simply using a timer.
"""

from __future__ import annotations

import time


class Scheduler:

    def __init__(

        self,

        interval: float = 0.75,

        minimum_notes: int = 4,

    ):

        self.interval = interval

        self.minimum_notes = minimum_notes

        self.last_run = 0.0

        self.last_note_count = 0

    # ----------------------------------------------------

    def should_generate(

        self,

        melody: list[int],

        current_chord,

        total_notes_seen: int | None = None,

    ) -> bool:

        now = time.perf_counter()

        # ----------------------------------------------
        # Not enough musical information yet.
        # ----------------------------------------------

        if len(melody) < self.minimum_notes:

            return False

        # ----------------------------------------------
        # No new notes since last generation.
        #
        # `melody` comes from a fixed-size rolling buffer
        # (MusicMemory has maxlen=32). Once that buffer is
        # full, len(melody) stops changing even though new
        # notes keep arriving (old notes are simply evicted).
        # We use a monotonically increasing "total notes
        # seen" counter instead, which keeps growing even
        # after the buffer caps out.
        # ----------------------------------------------

        note_count = (
            total_notes_seen
            if total_notes_seen is not None
            else len(melody)
        )

        if note_count == self.last_note_count:

            return False

        # ----------------------------------------------
        # Too soon.
        # ----------------------------------------------

        if now - self.last_run < self.interval:

            return False

        self.last_run = now

        self.last_note_count = note_count

        return True

    # ----------------------------------------------------

    def reset(self):

        self.last_run = 0.0

        self.last_note_count = 0

    # ----------------------------------------------------

    @property

    def seconds_until_next(self):

        return max(

            0.0,

            self.interval

            -

            (time.perf_counter() - self.last_run),

        )