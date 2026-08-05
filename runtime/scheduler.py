"""
scheduler.py

Musical scheduler for OmniAI.

Determines when the accompaniment
should generate a new harmony.
"""

from __future__ import annotations

import time


class Scheduler:

    def __init__(

        self,

        minimum_notes: int = 4,

        cooldown: float = 0.75,

    ):

        self.minimum_notes = minimum_notes

        self.cooldown = cooldown

        self.last_generation = 0.0

        self.last_note_count = 0

    # ---------------------------------------------------------

    def should_generate(

        self,

        melody: list[int],

        current_chord,

        total_notes_seen: int,

    ) -> bool:

        # ----------------------------
        # Need enough notes
        # ----------------------------

        if len(melody) < self.minimum_notes:

            return False

        # ----------------------------
        # Need at least one NEW note
        # ----------------------------

        if total_notes_seen == self.last_note_count:

            return False

        now = time.perf_counter()

        # ----------------------------
        # Cooldown
        # ----------------------------

        if (

            now - self.last_generation

            < self.cooldown

        ):

            return False

        self.last_generation = now

        self.last_note_count = total_notes_seen

        return True

    # ---------------------------------------------------------

    def reset(self):

        self.last_generation = 0.0

        self.last_note_count = 0

    # ---------------------------------------------------------

    @property

    def seconds_until_next(self):

        return max(

            0.0,

            self.cooldown

            -

            (

                time.perf_counter()

                -

                self.last_generation

            ),

        )