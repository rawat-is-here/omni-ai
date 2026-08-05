"""
realtime_synth.py

Continuous realtime synthesizer.

Unlike the previous implementation,
this version never renders whole chord
buffers.

The OutputStream callback itself
is the synthesizer.
"""

from __future__ import annotations

import threading

import numpy as np
import sounddevice as sd

from synth.voice_manager import VoiceManager


class RealtimeSynth:

    def __init__(

        self,

        sample_rate: int = 44100,

        block_size: int = 1024,

    ):

        self.sample_rate = sample_rate

        self.block_size = block_size

        self.voice_manager = VoiceManager(

            sample_rate=sample_rate,

        )

        self.master_gain = 0.75

        self.lock = threading.Lock()

        self.stream = sd.OutputStream(

            samplerate=self.sample_rate,

            channels=1,

            blocksize=self.block_size,

            callback=self.callback,

        )

        self.stream.start()

    # ---------------------------------------------------------

    def callback(

        self,

        outdata,

        frames,

        time_info,

        status,

    ):

        if status:

            print(status)

        with self.lock:

            audio = self.voice_manager.render(

                frames

            )

        peak = np.max(np.abs(audio))

        if peak > 1.0:

            audio /= peak

        audio *= self.master_gain

        outdata[:, 0] = audio.astype(np.float32)

    # ---------------------------------------------------------

    def set_chord(

        self,

        midi_notes: list[int],

        velocity: float = 1.0,

    ):

        with self.lock:

            self.voice_manager.set_chord(

                midi_notes,

                velocity,

            )

    # ---------------------------------------------------------

    def silence(self):

        with self.lock:

            self.voice_manager.clear()

    # ---------------------------------------------------------

    def stop(self):

        self.silence()

        self.stream.stop()

        self.stream.close()


# ------------------------------------------------------------

if __name__ == "__main__":

    import time

    synth = RealtimeSynth()

    print("Realtime synth running...")

    synth.set_chord([60, 64, 67])

    time.sleep(2)

    synth.set_chord([67, 71, 74])

    time.sleep(2)

    synth.set_chord([69, 72, 76])

    time.sleep(2)

    synth.stop()