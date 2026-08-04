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

    # -----------------------------------------------------

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


            fade = min(
                self.crossfade_samples,
                len(audio),
                len(old)
            )


            # blend old ending with new beginning

            transition = np.linspace(
                0,
                1,
                fade
            )


            audio[:fade] = (
                old[-fade:] * (1-transition)
                +
                audio[:fade] * transition
            )


            self.current_buffer = audio

            self.position = 0
    # -----------------------------------------------------

    def stop(self):

        self.stream.stop()

        self.stream.close()