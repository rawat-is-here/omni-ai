"""
Runtime Controller

Coordinates the complete OmniAI runtime.
"""

from __future__ import annotations

import time

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
        self.first_note_time = None
        self.key_votes = []  # List to store key guesses for majority voting
        
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

        self.key_detector = KeyDetector()

        self.progression_engine.active_key = None

        self.key_locked = False
        
        self.first_note_time = None
        
        self.key_votes = []
        if hasattr(self, '_last_vote_tick'):
            delattr(self, '_last_vote_tick')

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

    def update(self, timestamp: float | None = None):

        melody = self.current_melody()

        if not self.scheduler.should_generate(

            melody=melody,

            current_chord=self.current_chord,

            total_notes_seen=self.total_notes_seen,
            
            timestamp=timestamp,

        ):

            return

        # Real-time Key/Scale detection (8-second buffer with Majority Voting)
        if not self.key_locked and not self.memory.is_empty():
            current_time = timestamp if timestamp is not None else time.perf_counter()
            if self.first_note_time is None:
                self.first_note_time = current_time
                print("Singing detected! Starting 8-second scale analysis...")
                
            elapsed = current_time - self.first_note_time
            if elapsed >= 8.0:
                # Run the final vote count!
                if self.key_votes:
                    from collections import Counter
                    winner_key_str, count = Counter(self.key_votes).most_common(1)[0]
                    parts = winner_key_str.split()
                    tonic, mode = parts[0], parts[1]
                    
                    from core.data_models import KeyEstimate
                    winner_key = KeyEstimate(tonic=tonic, mode=mode, confidence=1.0)
                    
                    self.key_locked = True
                    self.progression_engine.update_key(winner_key)
                    print(
                        f"\n[Scale Locked] Key locked to -> {tonic} {mode} "
                        f"(Won majority: {count}/{len(self.key_votes)} votes over 8s buffer)"
                    )
                else:
                    # Fallback if no votes were cast (e.g. fast processing)
                    key_estimate = self.key_detector.detect(self.memory)
                    if key_estimate is not None:
                        self.key_locked = True
                        self.progression_engine.update_key(key_estimate)
                        print(
                            f"\n[Scale Locked] Key locked to -> {key_estimate.tonic} {key_estimate.mode} "
                            f"(conf: {key_estimate.confidence:.2f} based on fallback detect)"
                        )
            else:
                # Cast a vote once every second of singing
                vote_tick = int(elapsed)
                if not hasattr(self, '_last_vote_tick') or vote_tick > self._last_vote_tick:
                    self._last_vote_tick = vote_tick
                    key_estimate = self.key_detector.detect(self.memory)
                    if key_estimate is not None:
                        self.key_votes.append(f"{key_estimate.tonic} {key_estimate.mode}")
                
                # Limit printing to once per second
                if not hasattr(self, '_last_progress_print') or current_time - self._last_progress_print >= 1.0:
                    current_guess = self.key_votes[-1] if self.key_votes else "Unknown"
                    print(f"Analyzing scale... ({8.0 - elapsed:.1f}s remaining, current guess: {current_guess})")
                    self._last_progress_print = current_time

        # Remain silent during the initial 8-second analysis window
        if not self.key_locked:
            return

        forbidden = None
        force = None
        
        if not hasattr(self, 'first_chord_played'):
            self.first_chord_played = False
            
        if self.current_chord is not None:
            if not hasattr(self, 'chord_beat_count'):
                self.chord_beat_count = 0
            
            self.chord_beat_count += 1
            
            # If the current chord has been playing for 5-6 full beats, we forbid it for the next one
            if self.chord_beat_count >= 6:
                forbidden = self.current_chord
        elif not self.first_chord_played and self.key_locked and self.progression_engine.active_key is not None:
            # First chord after locking the scale should always be the Tonic
            qual = "" if self.progression_engine.active_key.mode == "Major" else "m"
            force = (self.progression_engine.active_key.tonic, qual)
            self.first_chord_played = True

        prediction = self.engine.process(

            melody,

            progression_engine=self.progression_engine,
            
            forbidden_chord=forbidden,
            
            force_chord=force

        )

        chord = (

            prediction["root"],

            prediction["quality"],

        )

        if chord != self.current_chord:

            print(

                "Chord ->",

                prediction["chord"],

            )

            self.current_chord = chord
            self.chord_beat_count = 1