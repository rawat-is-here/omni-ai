"""
session.py

Stores the current musical state of the
running OmniAI session.

This class is shared across the runtime so
different modules can access the current
musical context.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.data_models import (
    NoteEvent,
    ChordLabel,
)


@dataclass
class SessionState:
    """
    Current runtime state.
    """

    # -------------------------------
    # Melody
    # -------------------------------

    melody: list[NoteEvent] = field(default_factory=list)

    # -------------------------------
    # Harmony
    # -------------------------------

    current_chord: ChordLabel | None = None

    previous_chord: ChordLabel | None = None

    # -------------------------------
    # Musical Context
    # -------------------------------

    current_key: str | None = None

    current_mode: str | None = None

    tempo: float | None = None

    beat_position: float = 0.0

    # -------------------------------
    # Runtime
    # -------------------------------

    accompaniment_enabled: bool = True

    running: bool = True

    # ----------------------------------------------------

    def add_note(
        self,
        note: NoteEvent,
    ):

        self.melody.append(note)

    # ----------------------------------------------------

    def clear_melody(self):

        self.melody.clear()

    # ----------------------------------------------------

    def melody_notes(self):

        return [

            note.midi_note

            for note in self.melody

        ]

    # ----------------------------------------------------

    def set_chord(
        self,
        chord: ChordLabel,
    ):

        self.previous_chord = self.current_chord

        self.current_chord = chord

    # ----------------------------------------------------

    def stop(self):

        self.running = False

    # ----------------------------------------------------

    def reset(self):

        self.melody.clear()

        self.current_chord = None

        self.previous_chord = None

        self.current_key = None

        self.current_mode = None

        self.tempo = None

        self.beat_position = 0.0

        self.accompaniment_enabled = True

        self.running = True