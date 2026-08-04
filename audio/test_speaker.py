import numpy as np

from audio.speaker import Speaker

sr = 44100

duration = 2.0

t = np.linspace(
    0,
    duration,
    int(sr * duration),
    endpoint=False,
)

wave = 0.3 * np.sin(
    2 * np.pi * 440 * t
)

speaker = Speaker(sr)

print("Playing A4...")

speaker.play_blocking(wave)

print("Done.")