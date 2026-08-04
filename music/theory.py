"""
music/theory.py

Pure music theory helper functions.

Contains no runtime state.
"""

from __future__ import annotations

import math

NOTE_NAMES = (
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
)

NOTE_TO_INDEX = {
    n: i
    for i, n in enumerate(NOTE_NAMES)
}

MAJOR_SCALE = (0, 2, 4, 5, 7, 9, 11)

MINOR_SCALE = (0, 2, 3, 5, 7, 8, 10)

CHORD_INTERVALS = {

    "": (0, 4, 7),

    "m": (0, 3, 7),

    "7": (0, 4, 7, 10),

    "M7": (0, 4, 7, 11),

    "m7": (0, 3, 7, 10),

    "dim": (0, 3, 6),

    "aug": (0, 4, 8),
}
def midi_to_frequency(midi: int) -> float:
    return 440.0 * (2 ** ((midi - 69) / 12))


def frequency_to_midi(freq: float) -> int:
    return int(round(
        69 + 12 * math.log2(freq / 440.0)
    ))


def midi_to_note_name(midi: int) -> str:

    octave = (midi // 12) - 1

    return f"{NOTE_NAMES[midi % 12]}{octave}"


def note_name_to_index(note: str) -> int:

    return NOTE_TO_INDEX[note]


def pitch_class(midi: int) -> int:

    return midi % 12
def scale_notes(
    tonic: str,
    mode: str,
):

    root = NOTE_TO_INDEX[tonic]

    intervals = (
        MAJOR_SCALE
        if mode == "Major"
        else MINOR_SCALE
    )

    return [
        (root + i) % 12
        for i in intervals
    ]
def chord_notes(
    root: str,
    quality: str,
):

    root_pc = NOTE_TO_INDEX[root]

    intervals = CHORD_INTERVALS[quality]

    return [
        (root_pc + i) % 12
        for i in intervals
    ]
MODES = {
    "Ionian":     (0, 2, 4, 5, 7, 9, 11),   # Major
    "Dorian":     (0, 2, 3, 5, 7, 9, 10),
    "Phrygian":   (0, 1, 3, 5, 7, 8, 10),
    "Lydian":     (0, 2, 4, 6, 7, 9, 11),
    "Mixolydian": (0, 2, 4, 5, 7, 9, 10),
    "Aeolian":    (0, 2, 3, 5, 7, 8, 10),   # Natural Minor
    "Locrian":    (0, 1, 3, 5, 6, 8, 10),
}