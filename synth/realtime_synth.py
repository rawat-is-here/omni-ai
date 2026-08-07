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
from synth.effects import RTLowpassFilter, RTChorus, RTDelay, RTSchroederReverb


class RealtimeSynth:

    def __init__(

        self,

        sample_rate: int = 44100,

        block_size: int = 2048,

    ):

        self.sample_rate = sample_rate

        self.block_size = block_size

        self.voice_manager = VoiceManager(

            sample_rate=sample_rate,

        )

        self.master_gain = 0.75

        self.lock = threading.Lock()

        self.recording = False
        self.recorded_samples = []

        # Stateful Real-time Effects
        self.lowpass = RTLowpassFilter(cutoff_hz=1000.0, sample_rate=sample_rate)
        self.chorus = RTChorus(sample_rate=sample_rate, rate_hz=1.0, depth_ms=2.0, delay_ms=15.0, mix=0.35)
        self.delay_effect = RTDelay(delay_ms=250, feedback=0.4, mix=0.2, sample_rate=sample_rate)
        self.reverb_effect = RTSchroederReverb(sample_rate=sample_rate, feedback=0.75, mix=0.3)

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

        # Apply stateful real-time effects chain
        audio = self.lowpass.process(audio)
        audio = self.chorus.process(audio)
        audio = self.delay_effect.process(audio)
        audio = self.reverb_effect.process(audio)

        peak = np.max(np.abs(audio))

        if peak > 1.0:

            audio /= peak

        audio *= self.master_gain

        if self.recording:
            self.recorded_samples.append(np.copy(audio))

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

    # ---------------------------------------------------------

    def start_recording(self):
        with self.lock:
            self.recorded_samples = []
            self.recording = True
        print("\n[Recording Session Started]\n")

    # ---------------------------------------------------------

    def stop_recording(self, filepath):
        with self.lock:
            self.recording = False
            samples = self.recorded_samples
            self.recorded_samples = []

        if not samples:
            print("\n[Recording Session] No samples recorded.\n")
            return

        import wave
        # Concatenate all audio buffers
        full_audio = np.concatenate(samples)

        # Convert to 16-bit PCM
        pcm_data = (full_audio * 32767).astype(np.int16)

        with wave.open(filepath, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(pcm_data.tobytes())

        print(f"\n[Saved Session Recording] Saved to: {filepath}\n")


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