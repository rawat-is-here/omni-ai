"""
PyTorch Dataset for OmniAI.

Loads the serialized training samples and converts them
into tensors suitable for Transformer training.
"""

from __future__ import annotations

import pickle

import torch
from torch.utils.data import Dataset

from core.training_sample import TrainingSample

# Maximum melody length fed into the Transformer
MAX_SEQUENCE_LENGTH = 64

# Reserve token 0 for padding
PAD_TOKEN = 0


class OmniDataset(Dataset):

    def __init__(self, dataset_path: str, augment: bool = True):

        self.augment = augment

        with open(dataset_path, "rb") as f:
            self.samples: list[TrainingSample] = pickle.load(f)

    def __len__(self):

        return len(self.samples)

    def __getitem__(self, idx):

        sample = self.samples[idx]

        # ---------------------------------------
        # Shift MIDI notes by +1 so PAD = 0
        # and apply random key transposition
        # ---------------------------------------
        import random
        shift = random.randint(-5, 6) if self.augment else 0

        melody = [
            max(1, min(128, note + shift + 1))
            for note in sample.melody[:MAX_SEQUENCE_LENGTH]
        ]

        attention_mask = [1] * len(melody)

        if len(melody) < MAX_SEQUENCE_LENGTH:

            pad = MAX_SEQUENCE_LENGTH - len(melody)

            melody.extend([PAD_TOKEN] * pad)

            attention_mask.extend([0] * pad)

        return {

            "melody": torch.tensor(
                melody,
                dtype=torch.long,
            ),

            "mask": torch.tensor(
                attention_mask,
                dtype=torch.bool,
            ),

            "root": torch.tensor(
                (sample.root + shift) % 12,
                dtype=torch.long,
            ),

            "quality": torch.tensor(
                sample.quality,
                dtype=torch.long,
            ),

            "key": torch.tensor(
                (sample.key + shift) % 12,
                dtype=torch.long,
            ),

            "mode": torch.tensor(
                sample.mode,
                dtype=torch.long,
            ),
        }


if __name__ == "__main__":

    dataset = OmniDataset("models/train.pkl")

    print("=" * 60)
    print("Dataset Statistics")
    print("=" * 60)

    print("Samples:", len(dataset))

    sample = dataset[0]

    print()

    print("Melody Shape :", sample["melody"].shape)
    print("Mask Shape   :", sample["mask"].shape)

    print()

    print("Root         :", sample["root"])
    print("Quality      :", sample["quality"])
    print("Key          :", sample["key"])
    print("Mode         :", sample["mode"])

    print()

    print("First 20 Melody Tokens")

    print(sample["melody"][:20])

    print()

    print("First 20 Mask Values")

    print(sample["mask"][:20])