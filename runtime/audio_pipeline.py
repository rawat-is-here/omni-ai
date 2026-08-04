"""
Real-time audio pipeline.

Microphone
    ↓
Energy
    ↓
Voice Activity
    ↓
Pitch Detection
    ↓
Stable Note Detection
"""

from __future__ import annotations

from audio.audio_stream import AudioStream
from audio.energy_tracker import EnergyTracker
from audio.voice_activity import VoiceActivityDetector
from audio.pitch_tracker import PitchTracker

from music.note_tracker import NoteTracker


class AudioPipeline:

    def __init__(self):

        self.stream = AudioStream()

        self.energy = EnergyTracker()

        self.vad = VoiceActivityDetector()

        self.pitch = PitchTracker()

        self.note_tracker = NoteTracker()

    # -----------------------------------------------------

    def start(self):

        self.stream.start()

    # -----------------------------------------------------

    def stop(self):

        self.stream.stop()

    # -----------------------------------------------------

    def notes(self):
        """
        Infinite generator of NoteEvents.
        """

        for frame in self.stream.frames():

            # --------------------------
            # Energy
            # --------------------------

            energy = self.energy.process(frame)

            # --------------------------
            # Voice Activity
            # --------------------------

            voice = self.vad.process(energy)

            # --------------------------
            # Pitch
            # --------------------------

            pitch = self.pitch.process(
                frame,
                voice,
            )

            # --------------------------
            # Stable Note
            # --------------------------

            note = self.note_tracker.process(
                pitch
            )

            if note is not None:

                yield note