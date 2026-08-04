"""
Runtime Controller

Coordinates the complete OmniAI runtime.
"""

from __future__ import annotations

from music.music_memory import MusicMemory

from runtime.scheduler import Scheduler
from runtime.accompaniment_engine import AccompanimentEngine

from audio.speaker import Speaker


class RuntimeController:

    def __init__(self):
        
        self.current_chord = None

        self.memory = MusicMemory()

        self.scheduler = Scheduler()

        self.engine = AccompanimentEngine()

        self.speaker = Speaker()

        # Monotonically increasing counter of every note
        # ever added, independent of MusicMemory's rolling
        # (maxlen-capped) buffer. Used by the Scheduler to
        # detect "new notes" even after the buffer fills.
        self.total_notes_seen = 0

    # ----------------------------------------------------

    def add_note(self, note):

        self.memory.add(note)

        self.total_notes_seen += 1

    # ----------------------------------------------------

    def clear(self):
        

        self.memory.clear()

        self.scheduler.reset()
        
        self.current_chord = None

        self.total_notes_seen = 0

    # ----------------------------------------------------

    def current_melody(self):

        return [

            note.midi_note

            for note in self.memory.get_notes()

        ]

    # ----------------------------------------------------

    def update(self):
        """
        Called whenever a new NoteEvent arrives.
        """

        melody = self.current_melody()

        if not self.scheduler.should_generate(

            melody=melody,

            current_chord=self.current_chord,

            total_notes_seen=self.total_notes_seen,

        ):

            return
        print("Schedular allowed generation")
        print("Melody", melody)
        
        import time
        t0 = time.perf_counter()
        prediction = self.engine.predict(melody)
        print("Inference:", time.perf_counter()-t0)
        print("prediction", prediction)

        chord_id = (

            prediction["root"],

            prediction["quality"],

        )

        # -----------------------------------
        # Same harmony?
        # -----------------------------------

        

        self.current_chord = chord_id
        print("Rendering")

        harmony = self.engine.selector.build(
            prediction["root"],
            prediction["quality"],
        )

        notes = self.engine.synth.voice_leading.apply(harmony)

        self.speaker.play(notes)