"""
voice_manager.py

Maintains multiple continuously sounding voices
and allocates them with minimal movement.
"""

from __future__ import annotations

import numpy as np

from synth.voice import Voice


class VoiceManager:

    def __init__(

        self,

        voice_count: int = 4,

        sample_rate: int = 44100,

    ):

        self.voices = [

            Voice(sample_rate)

            for _ in range(voice_count)

        ]

    # ------------------------------------------------------------

    def clear(self):

        for voice in self.voices:

            voice.release_note()

    # ------------------------------------------------------------

    def active_notes(self):

        return [

            voice.current_note

            for voice in self.voices

        ]

    # ------------------------------------------------------------

    def set_chord(

        self,

        midi_notes: list[int],

        velocity: float = 0.9,

    ):

        midi_notes = sorted(midi_notes)

        assigned = set()

        # ----------------------------------------------------
        # Keep voices already on correct notes.
        # ----------------------------------------------------

        for voice in self.voices:

            if (

                voice.active

                and

                voice.current_note in midi_notes

            ):

                assigned.add(

                    voice.current_note

                )

        remaining = [

            note

            for note in midi_notes

            if note not in assigned

        ]

        # ----------------------------------------------------
        # Use inactive voices first.
        # ----------------------------------------------------

        inactive = [

            v

            for v in self.voices

            if not v.active

        ]

        while inactive and remaining:

            voice = inactive.pop(0)

            note = remaining.pop(0)

            voice.set_note(

                note,

                velocity,

            )

        # ----------------------------------------------------
        # Reassign closest existing voices.
        # ----------------------------------------------------

        while remaining:

            note = remaining.pop(0)

            candidates = [

                v

                for v in self.voices

                if (

                    v.current_note

                    not in midi_notes

                )

            ]

            if not candidates:

                break

            voice = min(

                candidates,

                key=lambda v:

                abs(

                    (v.current_note or note)

                    - note

                )

            )

            voice.set_note(

                note,

                velocity,

            )

        # ----------------------------------------------------
        # Release unused voices.
        # ----------------------------------------------------

        for voice in self.voices:

            if (

                voice.current_note

                is not None

                and

                voice.current_note

                not in midi_notes

            ):

                voice.release_note()

    # ------------------------------------------------------------

    def render(

        self,

        frames: int,

    ) -> np.ndarray:

        mix = np.zeros(

            frames,

            dtype=np.float32,

        )

        active = 0

        for voice in self.voices:

            audio = voice.render(

                frames,

            )

            mix += audio

            if voice.active:

                active += 1

        if active > 0:

            mix /= active

        peak = np.max(

            np.abs(mix)

        )

        if peak > 1.0:

            mix /= peak

        return mix