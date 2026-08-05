"""
scheduler.py

Musical scheduler for OmniAI.

Determines when the accompaniment
should generate a new harmony.
"""

import time
from music.beat_tracker import BeatTracker


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

        self.beat_tracker = BeatTracker()

    # ---------------------------------------------------------

    def register_note(self, note):
        """
        Register a newly detected note to update beat tracking phase and tempo.
        """
        self.beat_tracker.register_note_onset(note.start_time)

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
        # Hard Cooldown
        # ----------------------------

        if (

            now - self.last_generation

            < self.cooldown

        ):

            return False

        # ----------------------------
        # Beat Grid Synchronization
        # ----------------------------
        # If the beat tracker is active, wait until we hit a beat boundary
        if self.beat_tracker.anchor_time is not None:
            if not self.beat_tracker.is_on_beat(now, tolerance=0.18):
                return False

        self.last_generation = now

        self.last_note_count = total_notes_seen

        return True

    # ---------------------------------------------------------

    def reset(self):

        self.last_generation = 0.0

        self.last_note_count = 0

        self.beat_tracker = BeatTracker()

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