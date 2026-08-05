"""
Bollywood Synthetic Dataset Generator

Generates realistic singing melodies and corresponding chord progressions
focused on Bollywood soulful/romantic styles.
"""

from __future__ import annotations

import pickle
import random
from pathlib import Path

from core.training_sample import TrainingSample
from music.theory import CHORD_INTERVALS

# Key mappings
ROOTS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ROOT_TO_INDEX = {r: i for i, r in enumerate(ROOTS)}

# Scale definitions (semitones from tonic)
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]

# Quality mappings
QUALITY_TO_INDEX = {
    "": 0,
    "m": 1,
    "7": 2,
    "M7": 3,
    "m7": 4,
    "dim": 5,
    "aug": 6,
}

# Classic Bollywood soulful progressions
# Chords are specified as: (scale_degree, quality)
# Minor keys:
# - i - VI - III - VII (e.g. Am - F - C - G)
# - vi - IV - I - V (major scale equivalent)
# - i - v - VI - VII (e.g. Am - Em - F - G)
# - i - iv - VII - III (e.g. Am - Dm - G - C)
# - i - VI - III - V (Aeolian with secondary dominant resolve, e.g. Am - F - C - E)
# Major keys:
# - I - V - vi - IV (e.g. C - G - Am - F)
# - I - vi - IV - V (e.g. C - Am - F - G)
# - I - IV - V - IV (e.g. C - F - G - F)

BOLLYWOOD_PROGRESSIONS = [
    # Minor progressions
    {"mode": "minor", "chords": [(0, "m"), (5, ""), (2, ""), (6, "")]}, # i - VI - III - VII
    {"mode": "minor", "chords": [(0, "m"), (3, "m"), (6, ""), (2, "")]}, # i - iv - VII - III
    {"mode": "minor", "chords": [(0, "m"), (4, "m"), (5, ""), (6, "")]}, # i - v - VI - VII
    {"mode": "minor", "chords": [(0, "m"), (5, ""), (2, ""), (4, "")]}, # i - VI - III - V (E major/E7 resolution)
    
    # Major progressions
    {"mode": "major", "chords": [(0, ""), (4, ""), (5, "m"), (3, "")]}, # I - V - vi - IV
    {"mode": "major", "chords": [(5, "m"), (3, ""), (0, ""), (4, "")]}, # vi - IV - I - V
    {"mode": "major", "chords": [(0, ""), (5, "m"), (3, ""), (4, "")]}, # I - vi - IV - V
    {"mode": "major", "chords": [(0, ""), (3, ""), (4, ""), (3, "")]}, # I - IV - V - IV
]


def generate_vocal_melody(
    key_pc: int,
    scale_intervals: list[int],
    chord_root_pc: int,
    chord_quality: str,
    length: int = 8,
) -> list[int]:
    """
    Generates a natural, conjunct (step-wise) vocal melody over a chord.
    """
    intervals = CHORD_INTERVALS.get(chord_quality, (0, 4, 7))
    chord_tones = [(chord_root_pc + i) % 12 for i in intervals]
    scale_tones = [(key_pc + i) % 12 for i in scale_intervals]
    
    # Start on a chord tone in a comfortable singing range (Octave 4 or 5)
    curr_pc = random.choice(chord_tones)
    curr_octave = random.choice([4, 5])
    curr_midi = 12 * (curr_octave + 1) + curr_pc
    
    melody = [curr_midi]
    
    for _ in range(length - 1):
        # Walk step-wise in the scale, with occasional leaps
        step = random.choices([-2, -1, 0, 1, 2, -3, 3], weights=[10, 35, 10, 35, 10, 5, 5])[0]
        
        pc = curr_midi % 12
        if pc in scale_tones:
            idx = scale_tones.index(pc)
        else:
            idx = min(range(len(scale_tones)), key=lambda i: min(abs(scale_tones[i] - pc), 12 - abs(scale_tones[i] - pc)))
            
        new_idx = (idx + step) % len(scale_tones)
        new_pc = scale_tones[new_idx]
        
        new_octave = curr_octave
        if step > 0 and new_pc < pc:
            new_octave += 1
        elif step < 0 and new_pc > pc:
            new_octave -= 1
            
        # Clamp to vocal range: Octave 3 to 5 (MIDI 48 to 83)
        new_octave = max(3, min(5, new_octave))
        curr_midi = 12 * (new_octave + 1) + new_pc
        melody.append(curr_midi)
        curr_octave = new_octave
        
    return melody


def generate_dataset(num_samples: int = 120000) -> list[TrainingSample]:
    dataset = []
    
    for _ in range(num_samples):
        # Pick random key tonic and progression
        key_name = random.choice(ROOTS)
        key_pc = ROOT_TO_INDEX[key_name]
        
        prog = random.choice(BOLLYWOOD_PROGRESSIONS)
        scale_intervals = MAJOR_SCALE if prog["mode"] == "major" else MINOR_SCALE
        mode_idx = 0 if prog["mode"] == "major" else 1
        
        # Select a chord from this progression
        deg, qual = random.choice(prog["chords"])
        
        # Calculate chord root pitch class
        deg_interval = scale_intervals[deg]
        chord_root_pc = (key_pc + deg_interval) % 12
        
        # Generate melody (length between 4 and 10 notes)
        melody_len = random.randint(4, 10)
        melody = generate_vocal_melody(key_pc, scale_intervals, chord_root_pc, qual, melody_len)
        
        sample = TrainingSample(
            melody=melody,
            root=chord_root_pc,
            quality=QUALITY_TO_INDEX.get(qual, 0),
            key=key_pc,
            mode=mode_idx,
        )
        dataset.append(sample)
        
    return dataset


if __name__ == "__main__":
    print("Generating synthetic Bollywood dataset...")
    data = generate_dataset(120000)
    
    out_file = Path("models/bollywood_train.pkl")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_file, "wb") as f:
        pickle.dump(data, f)
        
    print(f"Generated {len(data)} samples and saved to {out_file}")
