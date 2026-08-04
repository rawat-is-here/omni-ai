"""
RealtimeSynth

Maintains a continuous output stream.

Instead of restarting the speakers every chord,
the newest chord is simply swapped in.
"""

from __future__ import annotations

import threading

import numpy as np
import sounddevice as sd

from synth.oscillators import OscillatorBank
from synth.effects import Effects
from synth.mixer import Mixer


class RealtimeSynth:

    def __init__(self, sample_rate=44100):

        self.sample_rate = sample_rate

        self.osc = OscillatorBank()
        self.fx = Effects()
        self.mixer = Mixer()

        self.current_buffer = np.zeros(
           self.sample_rate * 3,
           dtype=np.float32
        )

        self.position = 0

        self.crossfade_samples = int(
            0.08 * self.sample_rate
        )
        self.fade_samples = int(0.05 * self.sample_rate)

        self.lock = threading.Lock()
        self._debug_frames = []

        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self.callback,
            blocksize=1024,
        )

        self.stream.start()

    # -----------------------------------------------------

    def callback(self, outdata, frames, time, status):

        if status:
            print("Audio status:", status)

        with self.lock:

            outdata.fill(0)

            end = self.position + frames

            if self.position < len(self.current_buffer):

                chunk = self.current_buffer[
                    self.position:end
                ]

                length = len(chunk)

                outdata[:length,0] = chunk

                self.position += length


                # fade out near end of chord
                remaining = len(self.current_buffer) - self.position

                if remaining < self.fade_samples:

                    fade_length = min(
                        self.fade_samples,
                        length
                    )

                    fade = np.linspace(
                        1,
                        0,
                        fade_length
                    )

                    outdata[
                        length-fade_length:length,
                        0
                    ] *= fade
            self._debug_frames.append(outdata[:, 0].copy())
        

    # -----------------------------------------------------
    
    def save_debug_recording(self, path="debug_recording.wav"):
        from scipy.io import wavfile
        import numpy as np

        if not self._debug_frames:
            print("No audio captured yet.")
            return

        audio = np.concatenate(self._debug_frames)
        audio_int16 = np.clip(audio, -1.0, 1.0)
        audio_int16 = (audio_int16 * 32767).astype(np.int16)

        wavfile.write(path, self.sample_rate, audio_int16)
        print(f"Saved debug recording to {path}")

    def play_chord(self, notes, duration=3.0):

        audio = self.osc.chord(
            notes,
            duration
        )

        audio = self.fx.adsr(
            audio,
            attack=0.15,
            decay=0.20,
            sustain=0.85,
            release=0.40,
        )

        audio = self.fx.lowpass(audio)

        audio = self.fx.delay(audio)

        audio = self.fx.reverb(audio)

        audio = self.mixer.set_volume(
            audio,
            0.8
        )


        with self.lock:

            old = self.current_buffer


            # first chord
            if len(old) == 0 or np.max(np.abs(old)) == 0:

                self.current_buffer = audio
                self.position = 0
                return


            # Use the segment of `old` that is actually about
            # to be heard (right where playback currently is),
            # not the tail of the buffer — the tail has already
            # gone through its release and is near-silent, which
            # has nothing to do with what's playing right now.
            current_position = min(self.position, len(old))

            fade = min(
                self.crossfade_samples,
                len(audio),
                max(0, len(old) - current_position)
            )

            if fade > 0:

                outgoing = old[
                    current_position:current_position + fade
                ]

                # blend the currently-playing tail with the new beginning

                transition = np.linspace(
                    0,
                    1,
                    fade
                )

                audio[:fade] = (
                    outgoing * (1-transition)
                    +
                    audio[:fade] * transition
                )


            self.current_buffer = audio

            self.position = 0
    # -----------------------------------------------------

    def stop(self):
        self.save_debug_recording()

        self.stream.stop()

        self.stream.close()