from dataclasses import dataclass, field
from typing import Optional
import numpy as np


# ==========================================================
# Raw audio coming from microphone
# ==========================================================

@dataclass(slots=True)
class AudioFrame:
    """
    One chunk of audio captured from the microphone.
    """

    samples: np.ndarray
    sample_rate: int
    timestamp: float
    frame_index: int


# ==========================================================
# Voice Activity Detection Result
# ==========================================================

@dataclass(slots=True)
class VoiceActivityResult:
    """
    Result of voice activity detection.
    """

    is_voiced: bool
    confidence: float


# ==========================================================
# Energy Analysis
# ==========================================================

@dataclass(slots=True)
class EnergyResult:
    """
    Loudness statistics of one audio frame.
    """

    rms: float
    peak: float


# ==========================================================
# Pitch Detection
# ==========================================================

@dataclass(slots=True)
class PitchResult:
    """
    Pitch estimation for one audio frame.
    """

    frequency: float

    midi_note: Optional[int]

    note_name: Optional[str]

    octave: Optional[int]

    confidence: float

    voiced: bool


# ==========================================================
# Stable Musical Note
# ==========================================================

@dataclass(slots=True)
class NoteEvent:
    """
    Represents a musical note, not just an instantaneous pitch.
    """

    midi_note: int

    note_name: str

    start_time: float

    end_time: float

    confidence: float

    velocity: float

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


# ==========================================================
# Estimated Musical Key
# ==========================================================

@dataclass(slots=True)
class KeyEstimate:
    """
    Estimated musical key.
    """

    tonic: Optional[str]

    mode: Optional[str]

    confidence: float


# ==========================================================
# Chord Prediction
# ==========================================================

@dataclass(slots=True)
class ChordPrediction:
    """
    Output from the harmony engine.
    """

    chord_name: str

    confidence: float

    source: str = "AI"


@dataclass(slots=True)
class ScaleResult:

    mode: str

    confidence: float

    pitch_classes: tuple[int, ...]



@dataclass(slots=True)
class PhraseInfo:
    """
    Describes the current musical phrase.
    """

    note_count: int

    duration: float

    average_note_duration: float

    average_gap: float

    contour: str

    density: float

    phrase_complete: bool

    confidence: float
    


@dataclass(slots=True)
class RhythmInfo:
    """
    Describes rhythmic characteristics
    of the current musical phrase.
    """

    average_note_duration: float

    average_gap: float

    notes_per_second: float

    articulation: str

    rhythmic_stability: float
    


@dataclass(slots=True)
class HarmonyContext:

    recent_notes: list

    phrase_info: object | None

    rhythm_info: object | None

    scale_result: object | None

    key_result: object | None

    tempo: float | None

    beat_position: float | None
    

@dataclass(slots=True)
class HarmonyState:
    root: str
    quality: str
    inversion: int
    bass_note: int
    pitch_classes: tuple[int, ...]
    confidence: float
@dataclass(slots=True)

class ChordLabel:
    """
    One chord inside a song.
    """

    root: str

    quality: str

    notes: tuple[int, ...]

    start_time: float

    end_time: float

    confidence: float = 1.0

    @property
    def chord_name(self):
        return f"{self.root}{self.quality}"