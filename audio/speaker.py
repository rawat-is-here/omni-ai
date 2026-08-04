"""
Speaker

Continuous realtime speaker.
"""

from __future__ import annotations

from synth.realtime_synth import RealtimeSynth


class Speaker:

    def __init__(self):

        self.synth = RealtimeSynth()

    def play(self, notes):

        self.synth.play_chord(notes)

    def stop(self):

        self.synth.stop()