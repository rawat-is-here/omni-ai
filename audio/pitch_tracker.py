"""
Public pitch tracking interface.
"""

from audio.pitch.autocorrelation import (
    AutoCorrelationPitchDetector,
)


class PitchTracker:

    def __init__(self):

        self.detector = AutoCorrelationPitchDetector()

    def process(
        self,
        frame,
        voice,
    ):
        return self.detector.process(
            frame,
            voice,
        )