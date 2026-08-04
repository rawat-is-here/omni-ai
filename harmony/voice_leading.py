"""
Voice Leading

Chooses the smoothest chord inversion
to minimize note movement.
"""

from __future__ import annotations

from core.data_models import HarmonyState


class VoiceLeading:

    def __init__(self):

        self.previous_voicing: list[int] | None = None

    # ------------------------------------------------------------

    def apply(
        self,
        harmony: HarmonyState,
    ) -> list[int]:

        root = harmony.bass_note

        # Build root-position chord
        notes = [
            root + pc - (root % 12)
            for pc in harmony.pitch_classes
        ]

        # Ensure every note is above bass
        for i in range(len(notes)):

            while notes[i] < root:

                notes[i] += 12

        candidates = []

        # Root Position
        candidates.append(notes.copy())

        # First inversion
        inv1 = notes.copy()

        if len(inv1) >= 3:
            inv1[0] += 12
            inv1.sort()
            candidates.append(inv1)

        # Second inversion
        inv2 = notes.copy()

        if len(inv2) >= 3:
            inv2[0] += 12
            inv2[1] += 12
            inv2.sort()
            candidates.append(inv2)

        # Third inversion (7th chords)
        inv3 = notes.copy()

        if len(inv3) == 4:
            inv3[0] += 12
            inv3[1] += 12
            inv3[2] += 12
            inv3.sort()
            candidates.append(inv3)

        # First chord
        if self.previous_voicing is None:

            self.previous_voicing = candidates[0]

            harmony.inversion = 0

            return candidates[0]

        # Choose smallest movement
        best = None

        best_cost = 1e9

        best_inv = 0

        for inv, chord in enumerate(candidates):

            cost = 0

            for a, b in zip(

                self.previous_voicing,

                chord,

            ):

                cost += abs(a - b)

            if cost < best_cost:

                best_cost = cost

                best = chord

                best_inv = inv

        harmony.inversion = best_inv

        self.previous_voicing = best

        return best


# ------------------------------------------------------------

if __name__ == "__main__":

    from harmony.chord_selector import ChordSelector

    selector = ChordSelector()

    vl = VoiceLeading()

    progression = [

        ("C", ""),

        ("G", ""),

        ("Am", "m"),   # This line will be corrected below

        ("F", ""),

        ("C", ""),

    ]

    progression = [

        ("C", ""),

        ("G", ""),

        ("A", "m"),

        ("F", ""),

        ("C", ""),

    ]

    for root, quality in progression:

        state = selector.build(

            root,

            quality,

        )

        voicing = vl.apply(state)

        print()

        print(root + quality)

        print("Inversion:", state.inversion)

        print("Notes:", voicing)