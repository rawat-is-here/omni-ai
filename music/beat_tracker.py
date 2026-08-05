"""
music/beat_tracker.py

Real-time tempo and beat tracker.
Analyzes note onset times to estimate BPM and keep track of beat grid phase.
"""

from __future__ import annotations

import numpy as np


class BeatTracker:
    def __init__(self, default_bpm: float = 100.0):
        self.bpm = default_bpm
        self.beat_period = 60.0 / default_bpm
        self.anchor_time = None
        self.onset_times = []
        self.max_onsets = 16

    def register_note_onset(self, onset_time: float):
        """
        Registers a new note start time and updates tempo and phase alignment.
        """
        self.onset_times.append(onset_time)
        if len(self.onset_times) > self.max_onsets:
            self.onset_times.pop(0)

        # Estimate BPM if we have enough note onsets
        if len(self.onset_times) >= 4:
            diffs = []
            for i in range(1, len(self.onset_times)):
                diff = self.onset_times[i] - self.onset_times[i-1]
                # Vocal transitions are usually between 0.15s (eighth notes at 200BPM) and 2.0s
                if 0.15 <= diff <= 2.0:
                    diffs.append(diff)

            if diffs:
                # Normalize intervals to a common beat period base (e.g. 0.4s to 0.85s)
                normalized = []
                for d in diffs:
                    while d < 0.4:
                        d *= 2.0
                    while d > 0.85:
                        d /= 2.0
                    normalized.append(d)
                
                estimated_period = np.median(normalized)
                estimated_bpm = 60.0 / estimated_period
                
                # Smooth tempo tracking using a running average filter
                self.bpm = 0.80 * self.bpm + 0.20 * estimated_bpm
                self.beat_period = 60.0 / self.bpm

        # Align phase
        if self.anchor_time is None:
            self.anchor_time = onset_time
        else:
            time_since_anchor = onset_time - self.anchor_time
            num_beats = round(time_since_anchor / self.beat_period)
            expected_beat_time = self.anchor_time + num_beats * self.beat_period
            error = onset_time - expected_beat_time
            
            # Phase correction step (PLL)
            self.anchor_time += 0.25 * error

    def time_to_nearest_beat(self, current_time: float) -> float:
        if self.anchor_time is None:
            return 0.0
        time_since_anchor = current_time - self.anchor_time
        num_beats = round(time_since_anchor / self.beat_period)
        nearest_beat_time = self.anchor_time + num_beats * self.beat_period
        return abs(current_time - nearest_beat_time)

    def is_on_beat(self, current_time: float, tolerance: float = 0.18) -> bool:
        """
        Returns True if current_time is close to a beat boundary.
        """
        if self.anchor_time is None:
            return True
        return self.time_to_nearest_beat(current_time) <= tolerance

    def current_beat_position(self, current_time: float) -> float:
        """
        Returns the beat position (e.g. 0.0 to 4.0 in a 4-beat cycle).
        """
        if self.anchor_time is None:
            return 0.0
        time_since_anchor = current_time - self.anchor_time
        beat_idx = (time_since_anchor / self.beat_period) % 4.0
        return float(beat_idx)
