"""
voice_activity.py

State-based Voice Activity Detector.
"""

from __future__ import annotations

from collections import deque

from config import VOICE
from core.data_models import (
    EnergyResult,
    VoiceActivityResult,
)


class VoiceActivityDetector:
    """
    Detects whether the user is actively singing.

    Uses temporal smoothing to prevent rapid ON/OFF flickering.
    """

    def __init__(self):

        self._history = deque(maxlen=6)

        self._is_voiced = False

    def process(
        self,
        energy: EnergyResult,
    ) -> VoiceActivityResult:

        voiced = energy.rms >= VOICE.SILENCE_THRESHOLD

        self._history.append(voiced)

        voiced_frames = sum(self._history)

        confidence = voiced_frames / len(self._history)

        if not self._is_voiced:

            if confidence >= 0.60:
                self._is_voiced = True

        else:

            if confidence <= 0.25:
                self._is_voiced = False

        return VoiceActivityResult(
            is_voiced=self._is_voiced,
            confidence=confidence,
        )