from __future__ import annotations

from typing import List

from core.training_sample import TrainingSample
from core.data_models import NoteEvent, ChordLabel


NOTE_NAMES = [
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B"
]

QUALITIES = [
    "",
    "m",
    "7",
    "M7",
    "m7",
    "dim",
    "aug"
]


class SampleGenerator:
    """
    Converts one parsed POP909 song into hundreds of
    supervised training samples.

    Every chord becomes one training example.
    """

    WINDOW_SIZE = 16

    def __init__(self):
        pass

    def generate(
        self,
        melody: List[NoteEvent],
        chords: List[ChordLabel],
        key: int,
        mode: int,
    ) -> List[TrainingSample]:

        samples = []

        if len(chords) < 2:
            return samples

        melody = sorted(melody, key=lambda n: n.start_time)

        previous_roots = []

        for chord in chords:

            melody_window = self._melody_before_chord(
                melody,
                chord
            )

            if len(melody_window) == 0:
                continue

            previous = previous_roots[-4:]

            while len(previous) < 4:
                previous.insert(0, -1)

            sample = TrainingSample(

                melody=melody_window,

                previous_chords=previous,

                key=key,

                mode=mode,

                beat=0,

                target_root=NOTE_NAMES.index(chord.root),

                target_quality=self._quality_index(
                    chord.quality
                )

            )

            samples.append(sample)

            previous_roots.append(
                NOTE_NAMES.index(chord.root)
            )

        return samples

    def _melody_before_chord(
        self,
        melody,
        chord
    ):

        notes = []

        for note in melody:

            if note.start_time <= chord.start_time:
                notes.append(note.midi_note)

        notes = notes[-self.WINDOW_SIZE:]

        while len(notes) < self.WINDOW_SIZE:
            notes.insert(0, 0)

        return notes

    def _quality_index(self, quality):

        if quality in QUALITIES:
            return QUALITIES.index(quality)

        return 0