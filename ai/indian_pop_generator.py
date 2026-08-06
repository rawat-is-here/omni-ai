"""
Indian Pop Synthetic Dataset Generator
Generates realistic singing melodies and corresponding chord progressions
focused on Arijit Singh, Atif Aslam, KK, and Anuv Jain soulful pop styles.
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

# Core Progressions representing Arijit, Atif, KK, and Anuv Jain
# Format: (scale_degree, quality)
INDIAN_POP_PROGRESSIONS = [
    # 1. Arijit - Tum Hi Ho / Ae Dil Hai Mushkil Style (Minor Aeolian)
    {"mode": "minor", "chords": [(0, "m"), (5, ""), (2, ""), (6, "")]}, # i - VI - III - VII (Am - F - C - G)
    
    # 2. Atif Aslam - Tu Jaane Na / Tere Bin Style (Standard Pop Major)
    {"mode": "major", "chords": [(0, ""), (4, ""), (5, "m"), (3, "")]}, # I - V - vi - IV (C - G - Am - F)
    
    # 3. KK - Kya Mujhe Pyaar Hai / Tu Hi Meri Shab Hai Style (Minor-feel Rock Pop)
    {"mode": "minor", "chords": [(0, "m"), (5, ""), (2, ""), (4, "m")]}, # i - VI - III - v (Am - F - C - Em)
    
    # 4. Anuv Jain - Baarishein / Gul Style (Dreamy Indie Major)
    {"mode": "major", "chords": [(0, ""), (5, "m"), (3, ""), (4, "")]}, # I - vi - IV - V (C - Am - F - G)
    
    # 5. Arijit - Channa Mereya Style (Emotional Minor)
    {"mode": "minor", "chords": [(0, "m"), (6, ""), (5, ""), (6, "")]}, # i - VII - VI - VII (Am - G - F - G)
    
    # 6. KK - Yaaron Style (Simple Friend Anthem Major)
    {"mode": "major", "chords": [(0, ""), (4, ""), (3, ""), (4, "")]}, # I - V - IV - V (C - G - F - G)
    
    # 7. Atif Aslam - Tera Hone Laga Hoon Style
    {"mode": "major", "chords": [(0, ""), (5, "m"), (3, ""), (0, "")]}, # I - vi - IV - I (C - Am - F - C)
    
    # 8. Anuv Jain - Alag Aasmaan / Mazaak Style
    {"mode": "major", "chords": [(0, ""), (3, ""), (5, "m"), (4, "")]}, # I - IV - vi - V (C - F - Am - G)
]


def generate_vocal_melody(
    key_pc: int,
    scale_intervals: list[int],
    chord_root_pc: int,
    chord_quality: str,
    length: int = 8,
) -> list[int]:
    """
    Generates a natural vocal melody that strongly emphasizes chord tones,
    reducing dataset ambiguity so the model can train with high accuracy.
    """
    intervals = CHORD_INTERVALS.get(chord_quality, (0, 4, 7))
    chord_tones = [(chord_root_pc + i) % 12 for i in intervals]
    scale_tones = [(key_pc + i) % 12 for i in scale_intervals]
    
    # Start on a chord tone (root, 3rd, 5th) in comfortable range
    curr_pc = random.choice(chord_tones)
    curr_octave = random.choice([4, 5])
    curr_midi = 12 * (curr_octave + 1) + curr_pc
    
    melody = [curr_midi]
    
    for _ in range(length - 1):
        steps = [-2, -1, 0, 1, 2, -3, 3]
        step_weights = [10, 35, 10, 35, 10, 5, 5]
        
        pc = curr_midi % 12
        if pc in scale_tones:
            idx = scale_tones.index(pc)
        else:
            idx = min(range(len(scale_tones)), key=lambda i: min(abs(scale_tones[i] - pc), 12 - abs(scale_tones[i] - pc)))
            
        candidates = []
        weights = []
        
        for step, sw in zip(steps, step_weights):
            new_idx = (idx + step) % len(scale_tones)
            new_pc = scale_tones[new_idx]
            
            # Massive weight boost for chord tones to make the harmony clear
            weight = sw
            if new_pc in chord_tones:
                weight *= 10  # 10x preference for chord tones
                
            candidates.append((new_idx, new_pc, step))
            weights.append(weight)
            
        # Select next note based on weighted probabilities
        chosen_idx, chosen_pc, step = random.choices(candidates, weights=weights)[0]
        
        new_octave = curr_octave
        if step > 0 and chosen_pc < pc:
            new_octave += 1
        elif step < 0 and chosen_pc > pc:
            new_octave -= 1
            
        # Clamp to vocal range
        new_octave = max(3, min(5, new_octave))
        curr_midi = 12 * (new_octave + 1) + chosen_pc
        melody.append(curr_midi)
        curr_octave = new_octave
        
    return melody


def generate_dataset(num_samples: int = 120000) -> list[TrainingSample]:
    dataset = []
    
    for _ in range(num_samples):
        # Pick random key tonic and progression
        key_name = random.choice(ROOTS)
        key_pc = ROOT_TO_INDEX[key_name]
        
        prog = random.choice(INDIAN_POP_PROGRESSIONS)
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
    print("Generating Indian Pop dataset (Arijit, Atif, KK, Anuv Jain styles)...")
    data = generate_dataset(120000)
    
    out_file = Path("models/indian_pop_train.pkl")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_file, "wb") as f:
        pickle.dump(data, f)
        
    print(f"Successfully generated {len(data)} samples and saved to {out_file}")
