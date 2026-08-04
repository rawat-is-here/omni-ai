"""
POP909 Parser

Reads one POP909 song folder and converts it into
internal OmniAI objects.
"""

from __future__ import annotations

from pathlib import Path

import pretty_midi

from core.data_models import (
    NoteEvent,
    ChordLabel,
)

from parsers.chord_extractor import ChordExtractor


class POP909Parser:

    def __init__(self):

        self.chord_extractor = ChordExtractor()

    # ============================================================
    # PUBLIC
    # ============================================================

    def parse_song(
        self,
        song_folder: str | Path,
    ):

        song_folder = Path(song_folder)

        midi_file = song_folder / f"{song_folder.name}.mid"
        chord_file = song_folder / "chord_midi.txt"
        key_file = song_folder / "key_audio.txt"

        melody = self._read_melody(midi_file)

        chords = self._read_chords(chord_file)

        key = self._read_key(key_file)

        return {

            "melody": melody,

            "chords": chords,

            "key": key,

        }

    # ============================================================
    # Melody
    # ============================================================

    def _read_melody(
        self,
        midi_path: Path,
    ):

        midi = pretty_midi.PrettyMIDI(str(midi_path))

        notes = []

        for instrument in midi.instruments:

            if instrument.is_drum:
                continue

            for note in instrument.notes:

                note_name = pretty_midi.note_number_to_name(
                    note.pitch
                )

                notes.append(

                    NoteEvent(

                        midi_note=note.pitch,

                        note_name=note_name,

                        start_time=note.start,

                        end_time=note.end,

                        confidence=1.0,

                        velocity=note.velocity,

                    )

                )

        notes.sort(key=lambda x: x.start_time)

        return notes

    # ============================================================
    # Chords
    # ============================================================

    def _read_chords(
        self,
        chord_file: Path,
    ):

        chords = []

        if not chord_file.exists():
            return chords

        with open(chord_file) as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                parts = line.split()

                if len(parts) < 3:
                    continue

                start = float(parts[0])

                end = float(parts[1])

                chord_name = parts[2]

                label = self.chord_extractor.from_name(

                    chord_name,

                    start,

                    end,

                )

                if label is not None:
                    chords.append(label)

        return chords

    # ============================================================
    # Key
    # ============================================================

    def _read_key(
        self,
        key_file: Path,
    ):

        if not key_file.exists():
            return None

        with open(key_file) as f:

            return f.readline().strip()