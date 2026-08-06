"""
Training script for OmniAI.
"""

from __future__ import annotations

import torch
import torch.nn as nn

from torch.utils.data import DataLoader
from torch.optim import AdamW

from ai.datasets import OmniDataset
from ai.model import OmniModel

# ==========================================================
# Configuration
# ==========================================================

BATCH_SIZE = 64
EPOCHS = 20
LEARNING_RATE = 1e-4

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", DEVICE)

# ==========================================================
# Dataset
# ==========================================================

import pickle
import os

print("Loading datasets...")
dataset = OmniDataset("models/train.pkl", augment=True)

if os.path.exists("models/indian_pop_train.pkl"):
    print("Loading and merging Indian Pop dataset...")
    with open("models/indian_pop_train.pkl", "rb") as f:
        indian_pop_samples = pickle.load(f)
    dataset.samples.extend(indian_pop_samples)

print(f"Total training samples: {len(dataset)}")

loader = DataLoader(
    dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
)

# ==========================================================
# Model
# ==========================================================

model = OmniModel().to(DEVICE)

optimizer = AdamW(
    model.parameters(),
    lr=LEARNING_RATE,
)

criterion = nn.CrossEntropyLoss()

# ==========================================================
# Training Loop
# ==========================================================

def main():
    for epoch in range(EPOCHS):

        model.train()

        total_loss = 0

        for batch in loader:

            melody = batch["melody"].to(DEVICE)

            mask = batch["mask"].to(DEVICE)

            root = batch["root"].to(DEVICE)

            quality = batch["quality"].to(DEVICE)

            output = model(
                melody,
                mask,
            )

            root_loss = criterion(
                output["root"],
                root,
            )

            quality_loss = criterion(
                output["quality"],
                quality,
            )

            loss = root_loss + quality_loss

            optimizer.zero_grad()

            loss.backward()

            optimizer.step()

            total_loss += loss.item()

        average_loss = total_loss / len(loader)

        print(
            f"Epoch {epoch+1:02d} "
            f"Loss = {average_loss:.4f}"
        )

    # ==========================================================
    # Save Model
    # ==========================================================

    torch.save(
        model.state_dict(),
        "models/omni_model.pt",
    )

    print()

    print("Training Complete!")

    print("Model saved to models/omni_model.pt")


if __name__ == "__main__":
    main()