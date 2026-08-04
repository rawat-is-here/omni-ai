"""
Audio effects for OmniAI.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import lfilter

class Effects:

    # -----------------------------------------------------
    # ADSR Envelope
    # -----------------------------------------------------

    def adsr(

        self,

        signal,

        attack=0.02,

        decay=0.10,

        sustain=0.75,

        release=0.20,

        sample_rate=44100,

    ):

        signal = signal.copy()

        n = len(signal)

        attack_n = int(sample_rate * attack)

        decay_n = int(sample_rate * decay)

        release_n = int(sample_rate * release)

        sustain_n = max(

            0,

            n - attack_n - decay_n - release_n,

        )

        envelope = np.zeros(n)

        pos = 0

        # Attack
        if attack_n > 0:

            envelope[pos:pos+attack_n] = np.linspace(

                0,

                1,

                attack_n,

                endpoint=False,

            )

            pos += attack_n

        # Decay
        if decay_n > 0:

            envelope[pos:pos+decay_n] = np.linspace(

                1,

                sustain,

                decay_n,

                endpoint=False,

            )

            pos += decay_n

        # Sustain
        if sustain_n > 0:

            envelope[pos:pos+sustain_n] = sustain

            pos += sustain_n

        # Release
        if release_n > 0:

            envelope[pos:] = np.linspace(

                sustain,

                0,

                n-pos,

            )

        return signal * envelope

    # -----------------------------------------------------
    # Delay
    # -----------------------------------------------------

    def delay(

        self,

        signal,

        delay_ms=180,

        feedback=0.30,

        sample_rate=44100,

    ):

        delay_samples = int(
            sample_rate * delay_ms / 1000
        )

        output = signal.copy()

        gain = feedback
        k = 1

        while abs(gain) > 1e-5 and k * delay_samples < len(signal):

            shift = k * delay_samples

            output[shift:] += gain * signal[:-shift]

            gain *= feedback
            k += 1

        return output
    # -----------------------------------------------------
    # Simple Reverb
    # -----------------------------------------------------

    def reverb(

        self,

        signal,

        sample_rate=44100,

    ):

        output = signal.copy()

        taps = [

            (0.040,0.30),

            (0.070,0.20),

            (0.110,0.12),

        ]

        for seconds,gain in taps:

            d = int(seconds*sample_rate)

            output[d:] += gain*signal[:-d]

        peak = np.max(np.abs(output))

        if peak > 1:

            output /= peak

        return output

    # -----------------------------------------------------
    # Low-pass Filter
    # -----------------------------------------------------

    def lowpass(

        self,

        signal,

        alpha=0.08,

    ):

        b = [alpha]
        a = [1, -(1 - alpha)]

        return lfilter(b, a, signal)

if __name__ == "__main__":

    import soundfile as sf

    from synth.oscillators import OscillatorBank

    osc = OscillatorBank()

    fx = Effects()

    chord = osc.chord(

        [60,64,67],

        duration=3,

    )

    chord = fx.adsr(chord)

    chord = fx.lowpass(chord)

    chord = fx.delay(chord)

    chord = fx.reverb(chord)

    sf.write(

        "test_chord.wav",

        chord,

        44100,

    )

    print("Generated test_chord.wav")