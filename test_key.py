import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from music.key_detector import KeyDetector
from music.music_memory import MusicMemory
from core.data_models import NoteEvent

memory = MusicMemory()
memory.add_note(NoteEvent(midi_note=60, velocity=100, timestamp=0.0, duration=1.0, confidence=1.0)) # C
memory.add_note(NoteEvent(midi_note=64, velocity=100, timestamp=1.0, duration=1.0, confidence=1.0)) # E
memory.add_note(NoteEvent(midi_note=67, velocity=100, timestamp=2.0, duration=1.0, confidence=1.0)) # G

detector = KeyDetector()
estimate = detector.detect(memory)
print(f"Estimated Key: {estimate.tonic} {estimate.mode} with confidence {estimate.confidence}")
