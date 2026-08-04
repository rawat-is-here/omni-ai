"""
Audio Mixer
"""

from __future__ import annotations

import numpy as np


class Mixer:

    def __init__(self):

        pass

    # ---------------------------------------------------------

    def mix(self, *signals):

        if not signals:
            return np.array([], dtype=np.float32)

        length = max(len(s) for s in signals)

        output = np.zeros(length, dtype=np.float32)

        for signal in signals:

            padded = np.zeros(length, dtype=np.float32)

            padded[:len(signal)] = signal

            output += padded

        peak = np.max(np.abs(output))

        if peak > 1.0:

            output /= peak

        return output

    # ---------------------------------------------------------

    def set_volume(

        self,

        signal,

        volume=1.0,

    ):

        return signal * volume


if __name__ == "__main__":

    from synth.oscillators import OscillatorBank

    osc = OscillatorBank()

    mixer = Mixer()

    c = osc.chord([60, 64, 67], 2)

    g = osc.chord([55, 59, 62], 2)

    c = mixer.set_volume(c, 0.8)

    g = mixer.set_volume(g, 0.5)

    mix = mixer.mix(c, g)

    import soundfile as sf

    sf.write(

        "mixed.wav",

        mix,

        44100,

    )

    print("mixed.wav generated.")