"""
Chord Selector

Converts an AI chord prediction into
playable MIDI notes.
"""

from __future__ import annotations

from core.data_models import HarmonyState


INTERVALS = {

    "": (0, 4, 7),

    "m": (0, 3, 7),

    "7": (0, 4, 7, 10),

    "M7": (0, 4, 7, 11),

    "m7": (0, 3, 7, 10),

    "dim": (0, 3, 6),

    "aug": (0, 4, 8),

}

ROOT_TO_PC = {

    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,

}


class ChordSelector:

    def __init__(self):

        pass

    # --------------------------------------------------------

    def build(

        self,

        root: str,

        quality: str,

    ) -> HarmonyState:

        root_pc = ROOT_TO_PC[root]

        intervals = INTERVALS.get(

            quality,

            INTERVALS[""],

        )

        pitch_classes = tuple(

            (root_pc + i) % 12

            for i in intervals

        )

        bass_note = 48 + root_pc

        return HarmonyState(

            root=root,

            quality=quality,

            inversion=0,

            bass_note=bass_note,

            pitch_classes=pitch_classes,

            confidence=1.0,

        )


# ------------------------------------------------------------

if __name__ == "__main__":

    selector = ChordSelector()

    chord = selector.build(

        "C",

        "",

    )

    print(chord)

    chord = selector.build(

        "A",

        "m",

    )

    print(chord)

    chord = selector.build(

        "G",

        "7",

    )

    print(chord)