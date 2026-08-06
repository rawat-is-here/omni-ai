"""
Chord Testing Utility
Reads an offline WAV file, simulates live processing, and evaluates generated chords against ground truth.
"""
import sys
import os
import argparse
import numpy as np
import scipy.io.wavfile as wavfile

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock sounddevice to avoid opening sound outputs during offline evaluation
import sounddevice as sd
class MockStream:
    def __init__(self, *args, **kwargs): pass
    def start(self): pass
    def stop(self): pass
    def close(self): pass
sd.OutputStream = MockStream

from config import AUDIO
from audio.energy_tracker import EnergyTracker
from audio.voice_activity import VoiceActivityDetector
from audio.pitch_tracker import PitchTracker
from music.note_tracker import NoteTracker
from runtime.controller import RuntimeController


def evaluate_wav(wav_path: str, expected_chords: list[str], key: str = None):
    print(f"Loading {wav_path}...")
    
    if not os.path.exists(wav_path):
        print(f"Error: {wav_path} not found in root directory.")
        return

    sample_rate, data = wavfile.read(wav_path)
    
    if data.ndim > 1:
        data = data[:, 0]  # Take left channel
        
    if sample_rate != AUDIO.SAMPLE_RATE:
        print(f"Resampling audio from {sample_rate} Hz to {AUDIO.SAMPLE_RATE} Hz for accurate pitch tracking...")
        import scipy.signal as signal
        num_samples = int(len(data) * AUDIO.SAMPLE_RATE / sample_rate)
        data = signal.resample(data, num_samples)
        sample_rate = AUDIO.SAMPLE_RATE

    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    else:
        data = data.astype(np.float32)
        
    # Initialize pipeline components
    energy = EnergyTracker()
    vad = VoiceActivityDetector()
    pitch = PitchTracker()
    note_tracker = NoteTracker()
    
    controller = RuntimeController(fixed_key_str=key)
    
    generated_chords = []
    
    total_frames = len(data)
    block_size = AUDIO.BUFFER_SIZE
    
    from core.data_models import AudioFrame
    from music.theory import NOTE_NAMES
    
    print("Processing audio...")
    
    for i in range(0, total_frames, block_size):
        frame = data[i:i + block_size]
        if len(frame) < block_size:
            frame = np.pad(frame, (0, block_size - len(frame)))
            
        timestamp = i / sample_rate
        
        # Wrap in AudioFrame object
        audio_frame = AudioFrame(
            samples=frame,
            sample_rate=sample_rate,
            timestamp=timestamp,
            frame_index=i // block_size
        )
        
        # Audio Pipeline
        e = energy.process(audio_frame)
        voice = vad.process(e)
        p = pitch.process(audio_frame, voice)
        note = note_tracker.process(p, timestamp=timestamp)
        
        if note is not None:
            note_name = NOTE_NAMES[note.midi_note % 12]
            print(f"Detected Note: {note_name}{note.midi_note // 12 - 1} at {timestamp:.2f}s (duration: {note.duration:.2f}s, confidence: {note.confidence:.2f})")
            controller.add_note(note)
            
        # Update Controller
        controller.update(timestamp=timestamp)
        
        # Track chord changes
        if controller.current_chord is not None:
            chord_str = f"{controller.current_chord[0]}{controller.current_chord[1]}"
            if not generated_chords or generated_chords[-1] != chord_str:
                generated_chords.append(chord_str)
                
    controller.clear()
    
    print("\n--- RESULTS ---")
    print(f"Generated Chords: {generated_chords}")
    print(f"Expected Chords:  {expected_chords}")
    
    # Calculate strict index accuracy
    matches = 0
    min_len = min(len(generated_chords), len(expected_chords))
    
    if len(expected_chords) == 0:
        print("Accuracy: 0.00% (No expected chords)")
        return
        
    for gen, exp in zip(generated_chords[:min_len], expected_chords[:min_len]):
        if gen == exp:
            matches += 1
            
    strict_accuracy = (matches / max(len(expected_chords), len(generated_chords))) * 100
    
    # Calculate Longest Common Subsequence (LCS) for musical alignment accuracy
    # This prevents a 1-chord shift from ruining the entire score.
    m = len(generated_chords)
    n = len(expected_chords)
    L = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif generated_chords[i-1] == expected_chords[j-1]:
                L[i][j] = L[i-1][j-1] + 1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])
                
    lcs_len = L[m][n]
    lcs_accuracy = (lcs_len / max(m, n)) * 100 if max(m, n) > 0 else 0.0
    
    print(f"Strict Index-by-Index Accuracy: {strict_accuracy:.2f}% (Fails on small timing offsets)")
    print(f"Musical Alignment (LCS) Accuracy: {lcs_accuracy:.2f}% (Tracks structural correctness)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate generated chords against a ground truth WAV file.")
    parser.add_argument("wav_path", type=str, help="Path to the WAV file containing vocals in the root folder")
    parser.add_argument("expected_chords", type=str, help="Comma-separated list of expected chords (e.g. 'Am,F,C,G')")
    parser.add_argument("--key", type=str, default=None, help="Optional fixed key, e.g. 'C Major'")
    args = parser.parse_args()
    
    expected = [c.strip() for c in args.expected_chords.split(",") if c.strip()]
    evaluate_wav(args.wav_path, expected, args.key)
