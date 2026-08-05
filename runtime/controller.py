"""
Runtime Controller

Coordinates the complete OmniAI runtime.
"""

from __future__ import annotations

from music.music_memory import MusicMemory
from music.key_detector import KeyDetector
from harmony.progression_engine import ProgressionEngine

from runtime.scheduler import Scheduler
from runtime.accompaniment_engine import AccompanimentEngine


class RuntimeController:

    def __init__(self, fixed_key_str: str | None = None):

        self.memory = MusicMemory()

        self.scheduler = Scheduler()

        self.engine = AccompanimentEngine()

        self.key_detector = KeyDetector()

        self.progression_engine = ProgressionEngine()

        self.current_chord = None

        # Total notes ever received.
        # Unlike MusicMemory, this never resets
        # until clear() is called.
        self.total_notes_seen = 0
        
        self.fixed_key_str = fixed_key_str
        self.key_locked = False
        
        if fixed_key_str:
            parts = fixed_key_str.split()
            if len(parts) >= 2:
                tonic = parts[0]
                mode = " ".join(parts[1:]).capitalize()
                from core.data_models import KeyEstimate
                fixed_key = KeyEstimate(tonic=tonic, mode=mode, confidence=1.0)
                self.progression_engine.update_key(fixed_key)
                self.key_locked = True
                print(f"Key manually locked to: {tonic} {mode}")
            else:
                print(f"Warning: Invalid key format '{fixed_key_str}'. Use format like 'C Major'. Auto-detecting instead.")

    # ---------------------------------------------------------

    def add_note(self, note):

        self.memory.add(note)

        self.total_notes_seen += 1

        self.scheduler.register_note(note)

    # ---------------------------------------------------------

    def clear(self):

        self.memory.clear()

        self.scheduler.reset()

        self.engine.stop()

        self.current_chord = None

        self.total_notes_seen = 0
        
        if not self.fixed_key_str:
            self.key_locked = False
            self.progression_engine.update_key(None)

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

        # Real-time Key/Scale detection
        if not self.key_locked:
            key_estimate = self.key_detector.detect(self.memory)
            if key_estimate is not None:
                self.progression_engine.update_key(key_estimate)
                if key_estimate.confidence > 0.80:
                    self.key_locked = True
                    print(
                        f"Key auto-locked to → {key_estimate.tonic} {key_estimate.mode} "
                        f"(conf: {key_estimate.confidence:.2f})"
                    )
                elif key_estimate.confidence > 0.65:
                    print(
                        f"Detecting Key... {key_estimate.tonic} {key_estimate.mode} "
                        f"(conf: {key_estimate.confidence:.2f})"
                    )

        prediction = self.engine.process(

            melody,
            progression_engine=self.progression_engine,

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