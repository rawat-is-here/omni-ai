"""
harmony/progression_engine.py

Progression Engine for OmniAI.
Enforces music theory constraints, defines chord families, allows beautiful
non-diatonic "off chords" (secondary dominants, borrowed chords), and snaps
discordant predictions to the active scale.
"""

from __future__ import annotations

from core.data_models import HarmonyState, KeyEstimate
from music.theory import NOTE_TO_INDEX, NOTE_NAMES, CHORD_INTERVALS

# Diatonic scale degrees and chord qualities
# Values are (root_offset_from_key, quality)
DIATONIC_CHORDS = {
    "Major": [
        (0, ""),     # I (C)
        (2, "m"),    # ii (Dm)
        (4, "m"),    # iii (Em)
        (5, ""),     # IV (F)
        (7, ""),     # V (G)
        (9, "m"),    # vi (Am)
        (11, "dim")  # vii° (Bdim)
    ],
    "Minor": [
        (0, "m"),    # i (Am)
        (2, "dim"),  # ii° (Bdim)
        (3, ""),     # III (C)
        (5, "m"),    # iv (Dm)
        (7, "m"),    # v (Em)
        (8, ""),     # VI (F)
        (10, "")     # VII (G)
    ]
}

# Beautiful "Off Chords" allowed in Bollywood progressions (Stripped down for simplicity)
ALLOWED_OFF_CHORDS = {
    "Major": [
        (5, "m"),    # iv (F minor borrowed chord, highly emotive!)
        (5, "m7"),   # iv7 (Fm7)
    ],
    "Minor": [
        (7, ""),     # V (E Major dominant resolving to i - harmonic minor)
        (7, "7"),    # V7 (E7 dominant)
    ]
}


class ProgressionEngine:
    def __init__(self):
        self.active_key: KeyEstimate | None = None

    def update_key(self, key_estimate: KeyEstimate | None):
        self.active_key = key_estimate

    def filter_chord(self, root: str, quality: str) -> tuple[str, str]:
        """
        Takes a predicted chord and snaps it to the active chord family
        or allowed off-chords if it is discordant.
        """
        if self.active_key is None or self.active_key.tonic is None:
            return root, quality

        key_tonic = self.active_key.tonic
        key_mode = self.active_key.mode if self.active_key.mode in ["Major", "Minor"] else "Major"
        
        key_idx = NOTE_TO_INDEX[key_tonic]
        pred_root_idx = NOTE_TO_INDEX[root]
        
        import random
        
        # Calculate pitch offset of the predicted chord relative to the key
        rel_offset = (pred_root_idx - key_idx) % 12
        
        # 1. Check if it's a diatonic chord in the key
        diatonic_list = DIATONIC_CHORDS[key_mode]
        for offset, qual in diatonic_list:
            if rel_offset == offset and quality == qual:
                return root, quality
                
        # 2. Check if it's an allowed beautiful off-chord
        # User requested: Force diatonic ~97% of the time. Only allow special off-chords ~3% of the time
        # or when we really need it.
        allowed_list = ALLOWED_OFF_CHORDS[key_mode]
        for offset, qual in allowed_list:
            if rel_offset == offset and quality == qual:
                if random.random() > 0.97:
                    return root, quality
                else:
                    break # Skip returning it, let it snap to the nearest diatonic chord below

        # 3. Snap to the nearest diatonic chord based on pitch class overlap
        # Generate pitch classes for predicted chord
        pred_intervals = CHORD_INTERVALS.get(quality, (0, 4, 7))
        pred_pcs = set((pred_root_idx + i) % 12 for i in pred_intervals)
        
        best_diatonic_root = None
        best_diatonic_qual = None
        max_overlap = -1
        
        for offset, qual in diatonic_list:
            dia_root = (key_idx + offset) % 12
            dia_intervals = CHORD_INTERVALS.get(qual, (0, 4, 7))
            dia_pcs = set((dia_root + i) % 12 for i in dia_intervals)
            
            # Count common notes
            overlap = len(pred_pcs.intersection(dia_pcs))
            if overlap > max_overlap:
                max_overlap = overlap
                best_diatonic_root = NOTE_NAMES[dia_root]
                best_diatonic_qual = qual
                
        if best_diatonic_root is not None:
            return best_diatonic_root, best_diatonic_qual
            
        return root, quality
