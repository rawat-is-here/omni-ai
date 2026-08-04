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

    ) -> bool:

        now = time.perf_counter()

        # ----------------------------------------------
        # Not enough musical information yet.
        # ----------------------------------------------

        if len(melody) < self.minimum_notes:

            return False

        # ----------------------------------------------
        # No new notes since last generation.
        # ----------------------------------------------

        if len(melody) == self.last_note_count:

            return False

        # ----------------------------------------------
        # Too soon.
        # ----------------------------------------------

        if now - self.last_run < self.interval:

            return False

        self.last_run = now

        self.last_note_count = len(melody)

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