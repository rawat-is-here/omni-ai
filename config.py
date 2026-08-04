"""
Global configuration for OmniAI.

Every configurable value in the project should live here.
No magic numbers are allowed anywhere else.
"""

from dataclasses import dataclass


# ==========================================================
# Audio Configuration
# ==========================================================

@dataclass(frozen=True)
class AudioConfig:
    SAMPLE_RATE: int = 44100
    BUFFER_SIZE: int = 1024
    CHANNELS: int = 1
    LATENCY: str = "low"


# ==========================================================
# Voice Activity Detection
# ==========================================================

@dataclass(frozen=True)
class VoiceConfig:
    SILENCE_THRESHOLD: float = 0.005
    MIN_VOICE_CONFIDENCE: float = 0.60


# ==========================================================
# Pitch Detection
# ==========================================================

@dataclass(frozen=True)
class PitchConfig:
    MIN_FREQUENCY: float = 80.0
    MAX_FREQUENCY: float = 1000.0

    MIN_CORRELATION: float = 0.40

    MEDIAN_FILTER_SIZE: int = 3


# ==========================================================
# Note Tracking
# ==========================================================

@dataclass(frozen=True)
class NoteTrackerConfig:
    MAX_NOTE_GAP_MS: int = 120
    MIN_NOTE_DURATION_MS: int = 80


# ==========================================================
# Key Detection
# ==========================================================

@dataclass(frozen=True)
class KeyDetectionConfig:
    MEMORY_DECAY: float = 0.98


# ==========================================================
# Harmony Engine
# ==========================================================

@dataclass(frozen=True)
class HarmonyConfig:
    MIN_CHORD_DURATION: float = 2.0
    REQUIRED_STABLE_FRAMES: int = 12


# ==========================================================
# Synth
# ==========================================================

@dataclass(frozen=True)
class SynthConfig:
    MAX_VOLUME: float = 0.35

    ATTACK_RATE: float = 0.05

    RELEASE_RATE: float = 0.015


# ==========================================================
# Global Config Object
# ==========================================================

AUDIO = AudioConfig()

VOICE = VoiceConfig()

PITCH = PitchConfig()

NOTES = NoteTrackerConfig()

KEY = KeyDetectionConfig()

HARMONY = HarmonyConfig()

SYNTH = SynthConfig()