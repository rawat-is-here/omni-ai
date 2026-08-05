"""
glide.py

Smooth frequency interpolation.

Instead of jumping immediately from one
frequency to another, Glide moves toward
the target frequency gradually.
"""

from __future__ import annotations


class Glide:
    """
    Smooth frequency glide.

    Example

    261 Hz

        ↓

    440 Hz

    becomes

    261
    264
    268
    273
    ...
    440
    """

    def __init__(

        self,

        initial: float = 440.0,

        glide_time: float = 0.05,

        sample_rate: int = 44100,

    ):

        self.current = float(initial)

        self.target = float(initial)

        self.sample_rate = sample_rate

        self.glide_time = glide_time

        # Number of samples used for one glide
        self.samples = max(

            1,

            int(glide_time * sample_rate),

        )

    # ---------------------------------------------------------

    def set_target(

        self,

        frequency: float,

    ):

        self.target = float(frequency)

    # ---------------------------------------------------------

    def reset(

        self,

        frequency: float,

    ):

        self.current = float(frequency)

        self.target = float(frequency)

    # ---------------------------------------------------------

    def next_value(self) -> float:
        """
        Advance one sample toward the target frequency.
        """

        difference = self.target - self.current

        if abs(difference) < 1e-6:
            return self.current

        self.current += difference / self.samples

        return self.current

    # ---------------------------------------------------------

    @property
    def finished(self) -> bool:

        return abs(

            self.target - self.current

        ) < 1e-3