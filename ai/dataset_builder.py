"""
Dataset Builder

Builds the supervised training dataset from POP909.
"""

from __future__ import annotations

from pathlib import Path
import pickle

from parsers.pop909_parser import POP909Parser
from core.training_sample import TrainingSample

ROOT_TO_INDEX = {
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

QUALITY_TO_INDEX = {
    "": 0,
    "m": 1,
    "7": 2,
    "M7": 3,
    "m7": 4,
    "dim": 5,
    "aug": 6,
}


class DatasetBuilder:

    def __init__(self):

        self.parser = POP909Parser()

    # -------------------------------------------------------

    def scan_dataset(self, dataset_root):

        dataset_root = Path(dataset_root)

        songs = []

        for folder in sorted(dataset_root.iterdir()):

            if folder.is_dir():
                songs.append(folder)

        return songs

    # -------------------------------------------------------

    def build_dataset(self, dataset_root):

        songs = self.scan_dataset(dataset_root)

        print(f"\nFound {len(songs)} songs.\n")

        dataset = []

        for i, song in enumerate(songs):

            print(f"[{i+1}/{len(songs)}] {song.name}")

            try:

                parsed = self.parser.parse_song(song)

                samples = self.build_song_samples(parsed)

                dataset.extend(samples)

            except Exception as e:

                print("Skipped:", e)

        print()

        print("Total samples:", len(dataset))

        return dataset

    # -------------------------------------------------------

    def build_song_samples(self, parsed_song):

        melody = parsed_song["melody"]

        chords = parsed_song["chords"]

        samples = []

        for chord in chords:

            notes = [

                n

                for n in melody

                if n.start_time >= chord.start_time
                and n.start_time < chord.end_time

            ]

            if len(notes) < 2:
                continue

            melody_tokens = [

                n.midi_note

                for n in notes

            ]

            sample = TrainingSample(

                melody=melody_tokens,

                root=ROOT_TO_INDEX[chord.root],

                quality=QUALITY_TO_INDEX.get(

                    chord.quality,

                    0,

                ),

                key=0,

                mode=0,

            )

            samples.append(sample)

        return samples

    # -------------------------------------------------------

    def save_dataset(

        self,

        dataset,

        output_file,

    ):

        output_file = Path(output_file)

        output_file.parent.mkdir(

            parents=True,

            exist_ok=True,

        )

        with open(output_file, "wb") as f:

            pickle.dump(dataset, f)

        print()

        print("Saved dataset to")

        print(output_file)

        print()

        print("Samples:", len(dataset))


if __name__ == "__main__":

    builder = DatasetBuilder()

    dataset = builder.build_dataset(

        "datasets/POP909"

    )

    builder.save_dataset(

        dataset,

        "models/train.pkl",

    )