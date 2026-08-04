"""
energy_tracker.py

Computes signal energy statistics from an audio frame.
"""

from __future__ import annotations

import numpy as np

from core.data_models import AudioFrame, EnergyResult


class EnergyTracker:
    """
    Computes loudness information from incoming audio.
    """

    def process(self, frame: AudioFrame) -> EnergyResult:
        """
        Calculate RMS and Peak amplitude.
        """

        samples = frame.samples

        rms = float(np.sqrt(np.mean(samples ** 2)))

        peak = float(np.max(np.abs(samples)))

        return EnergyResult(
            rms=rms,
            peak=peak,
        )