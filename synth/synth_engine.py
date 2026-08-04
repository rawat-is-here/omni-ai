"""
Synth Engine

Converts HarmonyState into playable audio.
"""

from __future__ import annotations

import numpy as np

from core.data_models import HarmonyState

from harmony.voice_leading import VoiceLeading

from synth.oscillators import OscillatorBank
from synth.effects import Effects
from synth.mixer import Mixer


class SynthEngine:

    def __init__(self):

        self.osc = OscillatorBank()

        self.fx = Effects()

        self.mixer = Mixer()

        self.voice_leading = VoiceLeading()

    # ------------------------------------------------------------

    def render(

        self,

        harmony: HarmonyState,

        duration: float = 1.0,

    ) -> np.ndarray:

        # Smooth chord

        notes = self.voice_leading.apply(

            harmony

        )

        # Generate oscillators

        chord = self.osc.chord(

            notes,

            duration,

        )

        # Audio effects

        chord = self.fx.adsr(

            chord,

            attack=0.15,

            decay=0.20,

            sustain=0.85,

            release=0.40,

        )

        chord = self.fx.lowpass(chord)

        chord = self.fx.delay(chord)

        chord = self.fx.reverb(chord)

        chord = self.mixer.set_volume(

            chord,

            0.8,

        )

        return chord


# ------------------------------------------------------------

if __name__ == "__main__":

    import soundfile as sf

    from harmony.chord_selector import ChordSelector

    selector = ChordSelector()

    synth = SynthEngine()

    progression = [

        ("C",""),

        ("G",""),

        ("A","m"),

        ("F",""),

        ("C",""),

    ]

    audio = []

    for root, quality in progression:

        harmony = selector.build(

            root,

            quality,

        )

        chord = synth.render(

            harmony,

            duration=1.5,

        )

        audio.append(chord)

    final = np.concatenate(audio)

    sf.write(

        "progression.wav",

        final,

        44100,

    )

    print("progression.wav created.")