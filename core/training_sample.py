from dataclasses import dataclass


@dataclass(slots=True)
class TrainingSample:

    melody: list[int]

    root: int

    quality: int

    key: int

    mode: int