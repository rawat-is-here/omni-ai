"""
Loss functions for OmniAI.
"""

import torch.nn as nn


class HarmonyLoss(nn.Module):

    def __init__(self):

        super().__init__()

        self.root_loss = nn.CrossEntropyLoss()

        self.quality_loss = nn.CrossEntropyLoss()

    def forward(

        self,

        root_logits,

        quality_logits,

        root_target,

        quality_target,

    ):

        loss_root = self.root_loss(
            root_logits,
            root_target,
        )

        loss_quality = self.quality_loss(
            quality_logits,
            quality_target,
        )

        total = loss_root + loss_quality

        return total