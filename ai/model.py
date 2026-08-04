"""
Transformer model for OmniAI.

Predicts chord root and chord quality
from a melody sequence.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn


# ==========================================================
# Positional Encoding
# ==========================================================

class PositionalEncoding(nn.Module):

    def __init__(
        self,
        embedding_dim: int,
        max_length: int = 512,
    ):

        super().__init__()

        pe = torch.zeros(max_length, embedding_dim)

        position = torch.arange(
            0,
            max_length,
            dtype=torch.float,
        ).unsqueeze(1)

        div_term = torch.exp(

            torch.arange(
                0,
                embedding_dim,
                2,
            ).float()

            * (-math.log(10000.0) / embedding_dim)

        )

        pe[:, 0::2] = torch.sin(position * div_term)

        pe[:, 1::2] = torch.cos(position * div_term)

        pe = pe.unsqueeze(0)

        self.register_buffer("pe", pe)

    def forward(self, x):

        return x + self.pe[:, :x.size(1)]


# ==========================================================
# Omni Transformer
# ==========================================================

class OmniModel(nn.Module):

    def __init__(self):

        super().__init__()

        self.embedding = nn.Embedding(

            num_embeddings=129,

            embedding_dim=128,

            padding_idx=0,

        )

        self.position = PositionalEncoding(

            embedding_dim=128

        )

        encoder_layer = nn.TransformerEncoderLayer(

            d_model=128,

            nhead=8,

            dim_feedforward=512,

            dropout=0.1,

            batch_first=True,

        )

        self.encoder = nn.TransformerEncoder(

            encoder_layer,

            num_layers=4,

        )

        self.dropout = nn.Dropout(0.2)

        self.root_head = nn.Linear(

            128,

            12,

        )

        self.quality_head = nn.Linear(

            128,

            7,

        )

    # ------------------------------------------------------

    def forward(

        self,

        melody,

        mask,

    ):

        x = self.embedding(melody)

        x = self.position(x)

        x = self.encoder(

            x,

            src_key_padding_mask=~mask,

        )

        mask_float = mask.unsqueeze(-1).float()
        x = x*mask_float
        x = x.sum(dim=1) / mask_float.sum(dim = 1).clamp(min = 1.0)

        x = self.dropout(x)

        root = self.root_head(x)

        quality = self.quality_head(x)

        return {

            "root": root,

            "quality": quality,

        }


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    model = OmniModel()

    melody = torch.randint(

        0,

        129,

        (4, 64),

    )

    mask = melody != 0

    output = model(

        melody,

        mask,

    )

    print()

    print("Root logits")

    print(output["root"].shape)

    print()

    print("Quality logits")

    print(output["quality"].shape)