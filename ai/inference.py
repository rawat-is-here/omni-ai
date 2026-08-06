"""
Inference engine for OmniAI.

Loads the trained Transformer and predicts
the most likely accompaniment chord.
"""

from __future__ import annotations

import torch

from ai.model import OmniModel

ROOT_NAMES = [
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

QUALITY_NAMES = [
    "",
    "m",
    "7",
    "M7",
    "m7",
    "dim",
    "aug",
]


class OmniInference:

    def __init__(
        self,
        model_path: str = "models/omni_model.pt",
    ):

        self.device = torch.device(
            "cuda" if torch.cuda.is_available()
            else "cpu"
        )

        self.model = OmniModel().to(self.device)

        self.model.load_state_dict(

            torch.load(
                model_path,
                map_location=self.device,
            )

        )

        self.model.eval()

    # ----------------------------------------------------

    def predict(self, melody, forbidden_chord: tuple[str, str] = None):

        melody = melody[:64]

        melody = [n + 1 for n in melody]

        if len(melody) < 64:

            melody += [0] * (64 - len(melody))

        mask = [n != 0 for n in melody]

        melody = torch.tensor(
            melody,
            dtype=torch.long,
            device=self.device,
        ).unsqueeze(0)

        mask = torch.tensor(
            mask,
            dtype=torch.bool,
            device=self.device,
        ).unsqueeze(0)

        with torch.no_grad():

            output = self.model(

                melody,

                mask,

            )

        root_logits = output["root"][0]
        qual_logits = output["quality"][0]
        
        # Calculate joint probabilities (12x7)
        joint_logits = root_logits.unsqueeze(1) + qual_logits.unsqueeze(0)
        
        # Mask out the forbidden chord
        if forbidden_chord is not None:
            f_root, f_qual = forbidden_chord
            try:
                r_idx = ROOT_NAMES.index(f_root)
                q_idx = QUALITY_NAMES.index(f_qual)
                joint_logits[r_idx, q_idx] = -float('inf')
            except ValueError:
                pass

        flat_idx = joint_logits.argmax().item()
        root = flat_idx // 7
        quality = flat_idx % 7

        return {

            "root_index": root,

            "quality_index": quality,

            "root": ROOT_NAMES[root],

            "quality": QUALITY_NAMES[quality],

            "chord": ROOT_NAMES[root] + QUALITY_NAMES[quality],

        }


# ------------------------------------------------------------

if __name__ == "__main__":

    ai = OmniInference()

    melody = [

        60,

        62,

        64,

        65,

        67,

        69,

        71,

        72,

    ]

    result = ai.predict(melody)

    print(result)