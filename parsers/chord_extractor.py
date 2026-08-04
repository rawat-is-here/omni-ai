"""
Chord Extractor

Converts POP909 chord strings into OmniAI ChordLabel objects.
"""

from __future__ import annotations

from core.data_models import ChordLabel

NOTE_NAMES = [
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
]

# Flats → Sharps
ENHARMONIC = {
    "Db": "C#",
    "Eb": "D#",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
}

# Chord intervals
CHORD_PATTERNS = {
    "": (0, 4, 7),
    "m": (0, 3, 7),
    "7": (0, 4, 7, 10),
    "M7": (0, 4, 7, 11),
    "m7": (0, 3, 7, 10),
    "dim": (0, 3, 6),
    "aug": (0, 4, 8),
}


class ChordExtractor:

    def __init__(self):
        pass

    # ==========================================================
    # PUBLIC
    # ==========================================================

    def from_name(
        self,
        chord_name: str,
        start_time: float,
        end_time: float,
    ) -> ChordLabel | None:
        """
        Example inputs:

        C:maj
        C:min
        D:maj7
        A:min7
        G:7
        N
        """

        chord_name = chord_name.strip()

        if chord_name in ("N", "None", ""):
            return None

        if ":" in chord_name:
            root, quality = chord_name.split(":")
        else:
            root = chord_name
            quality = "maj"

        root = ENHARMONIC.get(root, root)

        quality = self._normalize_quality(quality)

        if root not in NOTE_NAMES:
            return None

        intervals = CHORD_PATTERNS.get(
            quality,
            CHORD_PATTERNS[""],
        )

        root_pc = NOTE_NAMES.index(root)

        notes = tuple(
            (root_pc + i) % 12
            for i in intervals
        )

        return ChordLabel(
            root=root,
            quality=quality,
            notes=notes,
            start_time=start_time,
            end_time=end_time,
            confidence=1.0,
        )

    # ==========================================================
    # PRIVATE
    # ==========================================================

    def _normalize_quality(
        self,
        quality: str,
    ) -> str:

        quality = quality.lower()

        mapping = {

            "maj": "",

            "major": "",

            "min": "m",

            "minor": "m",

            "maj7": "M7",

            "major7": "M7",

            "min7": "m7",

            "minor7": "m7",

            "7": "7",

            "dim": "dim",

            "hdim7": "dim",

            "dim7": "dim",

            "aug": "aug",

            "+": "aug",

        }

        return mapping.get(quality, "")