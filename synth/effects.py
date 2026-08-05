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


class RTLowpassFilter:
    def __init__(self, cutoff_hz=1000.0, sample_rate=44100):
        self.sample_rate = sample_rate
        self.zi = np.zeros(2, dtype=np.float32)
        self.set_cutoff(cutoff_hz)

    def set_cutoff(self, cutoff_hz):
        from scipy.signal import butter
        self.b, self.a = butter(2, cutoff_hz, fs=self.sample_rate, btype='low')

    def process(self, block: np.ndarray) -> np.ndarray:
        from scipy.signal import lfilter
        y, self.zi = lfilter(self.b, self.a, block, zi=self.zi)
        return y.astype(np.float32)


class RTChorus:
    def __init__(self, sample_rate=44100, rate_hz=1.0, depth_ms=2.0, delay_ms=15.0, mix=0.35):
        self.sample_rate = sample_rate
        self.rate = rate_hz
        self.depth = depth_ms * sample_rate / 1000.0
        self.base_delay = delay_ms * sample_rate / 1000.0
        self.mix = mix
        
        max_delay = int(self.base_delay + self.depth + 10)
        self.buffer = np.zeros(max_delay * 2, dtype=np.float32)
        self.write_idx = 0
        self.lfo_phase = 0.0

    def process(self, block: np.ndarray) -> np.ndarray:
        n = len(block)
        out = np.empty(n, dtype=np.float32)
        buf_len = len(self.buffer)
        
        lfo_inc = 2.0 * np.pi * self.rate / self.sample_rate
        
        for i in range(n):
            self.buffer[self.write_idx] = block[i]
            
            mod = np.sin(self.lfo_phase)
            self.lfo_phase += lfo_inc
            if self.lfo_phase >= 2.0 * np.pi:
                self.lfo_phase -= 2.0 * np.pi
                
            curr_delay = self.base_delay + self.depth * mod
            read_idx_f = self.write_idx - curr_delay
            
            read_idx_low = int(np.floor(read_idx_f)) % buf_len
            read_idx_high = (read_idx_low + 1) % buf_len
            frac = read_idx_f - np.floor(read_idx_f)
            
            delayed_val = (1.0 - frac) * self.buffer[read_idx_low] + frac * self.buffer[read_idx_high]
            
            out[i] = (1.0 - self.mix) * block[i] + self.mix * delayed_val
            
            self.write_idx = (self.write_idx + 1) % buf_len
            
        return out


class RTDelay:
    def __init__(self, delay_ms=250, feedback=0.4, mix=0.2, sample_rate=44100):
        self.delay_samples = int(sample_rate * delay_ms / 1000)
        self.feedback = feedback
        self.mix = mix
        self.buffer = np.zeros(self.delay_samples, dtype=np.float32)
        self.write_idx = 0

    def process(self, block: np.ndarray) -> np.ndarray:
        n = len(block)
        output = np.empty(n, dtype=np.float32)
        buf_len = len(self.buffer)
        
        for i in range(n):
            delayed_sample = self.buffer[self.write_idx]
            output[i] = block[i] + self.mix * delayed_sample
            self.buffer[self.write_idx] = block[i] + self.feedback * delayed_sample
            self.write_idx = (self.write_idx + 1) % buf_len
            
        return output


class RTCombFilter:
    def __init__(self, delay_samples, feedback):
        self.buffer = np.zeros(delay_samples, dtype=np.float32)
        self.write_idx = 0
        self.feedback = feedback

    def process(self, block: np.ndarray) -> np.ndarray:
        n = len(block)
        out = np.empty(n, dtype=np.float32)
        buf_len = len(self.buffer)
        for i in range(n):
            delayed = self.buffer[self.write_idx]
            out[i] = delayed
            self.buffer[self.write_idx] = block[i] + self.feedback * delayed
            self.write_idx = (self.write_idx + 1) % buf_len
        return out


class RTAllPassFilter:
    def __init__(self, delay_samples, gain):
        self.buffer = np.zeros(delay_samples, dtype=np.float32)
        self.write_idx = 0
        self.gain = gain

    def process(self, block: np.ndarray) -> np.ndarray:
        n = len(block)
        out = np.empty(n, dtype=np.float32)
        buf_len = len(self.buffer)
        for i in range(n):
            x = block[i]
            delayed = self.buffer[self.write_idx]
            y = -self.gain * x + delayed
            out[i] = y
            self.buffer[self.write_idx] = x + self.gain * y
            self.write_idx = (self.write_idx + 1) % buf_len
        return out


class RTSchroederReverb:
    def __init__(self, sample_rate=44100, feedback=0.75, mix=0.3):
        self.mix = mix
        # Classic Schroeder comb delay times in seconds
        cf_times = [0.0297, 0.0371, 0.0411, 0.0437]
        # Schroeder allpass delay times in seconds
        ap_times = [0.0050, 0.0017]
        
        self.combs = [
            RTCombFilter(int(t * sample_rate), feedback)
            for t in cf_times
        ]
        self.allpasses = [
            RTAllPassFilter(int(t * sample_rate), 0.5)
            for t in ap_times
        ]

    def process(self, block: np.ndarray) -> np.ndarray:
        comb_sum = np.zeros(len(block), dtype=np.float32)
        for comb in self.combs:
            comb_sum += comb.process(block)
        comb_sum /= len(self.combs)
        
        out = comb_sum
        for ap in self.allpasses:
            out = ap.process(out)
            
        return (1.0 - self.mix) * block + self.mix * out


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