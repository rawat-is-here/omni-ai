"""
Runtime Controller

Coordinates the complete OmniAI runtime.
"""

from __future__ import annotations

from music.music_memory import MusicMemory

from runtime.scheduler import Scheduler
from runtime.accompaniment_engine import AccompanimentEngine


class RuntimeController:

    def __init__(self):

        self.memory = MusicMemory()

        self.scheduler = Scheduler()

        self.engine = AccompanimentEngine()

        self.current_chord = None

        # Total notes ever received.
        # Unlike MusicMemory, this never resets
        # until clear() is called.
        self.total_notes_seen = 0

    # ---------------------------------------------------------

    def add_note(self, note):

        self.memory.add(note)

        self.total_notes_seen += 1

    # ---------------------------------------------------------

    def clear(self):

        self.memory.clear()

        self.scheduler.reset()

        self.engine.stop()

        self.current_chord = None

        self.total_notes_seen = 0

    # ---------------------------------------------------------

    def current_melody(self):

        return [

            note.midi_note

            for note in self.memory.get_notes()

        ]

    # ---------------------------------------------------------

    def update(self):

        melody = self.current_melody()

        if not self.scheduler.should_generate(

            melody=melody,

            current_chord=self.current_chord,

            total_notes_seen=self.total_notes_seen,

        ):

            return

        prediction = self.engine.process(

            melody,

        )

        chord = (

            prediction["root"],

            prediction["quality"],

        )

        if chord != self.current_chord:

            print(

                "Chord →",

                prediction["chord"],

            )

            self.current_chord = chord