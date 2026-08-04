"""
midi_parser.py

Low-level MIDI parser.

Responsibilities
----------------
1. Load MIDI files
2. Read tempo & time signature
3. Convert note events into NoteEvent objects
4. Return parsed notes for downstream AI modules
"""

from __future__ import annotations

from pathlib import Path
from collections import defaultdict

import mido

from core.data_models import NoteEvent


DEFAULT_TEMPO = 500000  # 120 BPM


class MidiParser:

    def __init__(self):
        pass

    # --------------------------------------------------------
    # Load MIDI
    # --------------------------------------------------------

    def load(self, midi_path: str | Path):

        midi_path = Path(midi_path)

        if not midi_path.exists():
            raise FileNotFoundError(midi_path)

        return mido.MidiFile(midi_path)

    # --------------------------------------------------------
    # Debug
    # --------------------------------------------------------

    def print_tracks(self, midi):

        print("=" * 70)

        print(f"Tracks : {len(midi.tracks)}")

        print(f"Ticks Per Beat : {midi.ticks_per_beat}")

        print("=" * 70)

        for i, track in enumerate(midi.tracks):

            print(f"\nTrack {i}")

            for msg in track:
                print(msg)

    # --------------------------------------------------------
    # Parse Note Events
    # --------------------------------------------------------

    def parse_notes(self, midi):

        ticks_per_beat = midi.ticks_per_beat

        tempo = DEFAULT_TEMPO

        absolute_tick = 0

        active_notes = defaultdict(list)

        parsed_notes = []

        for msg in mido.merge_tracks(midi.tracks):

            absolute_tick += msg.time

            if msg.is_meta:

                if msg.type == "set_tempo":
                    tempo = msg.tempo

                continue

            current_time = mido.tick2second(
                absolute_tick,
                ticks_per_beat,
                tempo,
            )

            # -----------------------------

            if msg.type == "note_on" and msg.velocity > 0:

                active_notes[msg.note].append(
                    (
                        current_time,
                        msg.velocity,
                    )
                )

            # -----------------------------

            elif (
                msg.type == "note_off"
                or (
                    msg.type == "note_on"
                    and msg.velocity == 0
                )
            ):

                if not active_notes[msg.note]:
                    continue

                start_time, velocity = active_notes[msg.note].pop()

                duration = current_time - start_time

                parsed_notes.append(

                    NoteEvent(

                        midi_note=msg.note,

                        velocity=velocity,

                        start_time=start_time,

                        end_time=current_time,

                        duration=duration,

                        confidence=1.0,
                    )
                )

        parsed_notes.sort(key=lambda x: x.start_time)

        return parsed_notes


if __name__ == "__main__":

    parser = MidiParser()

    midi_path = input("Enter MIDI path: ").strip()

    midi = parser.load(midi_path)

    parser.print_tracks(midi)

    notes = parser.parse_notes(midi)

    print("\n")

    print("=" * 70)

    print(f"Parsed {len(notes)} notes")

    print("=" * 70)

    for note in notes[:20]:

        print(
            f"Note {note.midi_note:3} | "
            f"Vel {note.velocity:3} | "
            f"Start {note.start_time:7.3f} | "
            f"End {note.end_time:7.3f}"
        )