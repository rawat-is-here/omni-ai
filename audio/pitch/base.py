"""
Base classes for pitch detection algorithms.

Every pitch detector must inherit from PitchDetector.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.data_models import AudioFrame
from core.data_models import VoiceActivityResult
from core.data_models import PitchResult


class PitchDetector(ABC):
    """
    Abstract base class for every pitch detector.
    """

    @abstractmethod
    def process(
        self,
        frame: AudioFrame,
        voice: VoiceActivityResult,
    ) -> PitchResult:
        """
        Estimate the pitch of one audio frame.

        Returns
        -------
        PitchResult
        """
        raise NotImplementedError