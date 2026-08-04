"""
Utility functions.
"""

import torch


def save_checkpoint(model, optimizer, epoch, loss, filename):

    torch.save(
        {
            "epoch": epoch,
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "loss": loss,
        },
        filename,
    )


def load_checkpoint(model, optimizer, filename):

    checkpoint = torch.load(filename)

    model.load_state_dict(checkpoint["model_state"])

    optimizer.load_state_dict(checkpoint["optimizer_state"])

    return checkpoint["epoch"], checkpoint["loss"]